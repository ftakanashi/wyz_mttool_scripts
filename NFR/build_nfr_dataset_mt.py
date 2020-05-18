#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
This script can accept a query file and build a augmented source corpus file by using SetSimilaritySearch and EditDistance.
'''

import argparse
import editdistance
import queue
import time
from tqdm import tqdm
from SetSimilaritySearch import SearchIndex as SI
from multiprocessing import Process, Lock, JoinableQueue, Manager


def distance_score(a, b):
    '''
    The original editdistance library only return an absolute distance figure.
    Change it into a edit distance score which measures how similar between a & b by evaluating the edit distance
    FOR CHANGING a INTO b.
    reference: https://arxiv.org/pdf/1505.05841.pdf
    '''
    distance = editdistance.eval(a, b)
    set_len = len(list(set(a)))
    ed = max(1 - float(distance) / set_len, 0)
    return ed


def match_fuzzy(query, search_index, opt):
    '''
    Do a primary search by SetSimilaritySearch(SSS)
    :param query:
    :param search_index:
    :param opt:
    :return:
    '''
    if type(query) is not list:
        query = query.strip().split()
    query = set(query)    # SSS requires query to be unique

    if opt.include_perfect_match:
        flag = 99999
    else:
        flag = 1.0
    cand_indices = [t[0] for t in list(sorted(search_index.query(query), key=lambda x: x[1], reverse=True)) if
                    t[1] < flag]

    return cand_indices[:opt.sss_nbest]


def calc_edit_distance(query, cand_indices, tms_lines, opt):
    candidates = [tms_lines[i].strip().split() for i in cand_indices]
    res = {}
    if type(query) is not list:
        query = query.strip().split()
    for i, c in enumerate(candidates):
        ed_score = distance_score(query, c)
        if ed_score >= opt.ed_lambda:
            res[cand_indices[i]] = distance_score(query, c)

    return sorted(res, key=lambda x: res[x], reverse=True)


class QueryWorker(Process):
    def __init__(self, p_name, queue, lock, **kwargs):
        super(QueryWorker, self).__init__()
        self.p_name = p_name
        self.queue = queue
        self.lock = lock
        self.search_index = kwargs.get('search_index')
        self.opt = kwargs.get('opt')
        self.tms_lines = kwargs.get('tms_lines')
        self.tmt_lines = kwargs.get('tmt_lines')
        self.cache = kwargs.get('cache')
        self.res_container = kwargs.get('res_container')

    def concat_process(self, q_i, query, query_target):
        if query not in self.cache:
            cand_indices = match_fuzzy(query, self.search_index, self.opt)
            cand_indices = calc_edit_distance(query, cand_indices, self.tms_lines, self.opt)
            appendix = []
            for i in range(self.opt.format_n):
                try:
                    tmt_i = cand_indices[i]
                except IndexError as e:
                    appendix.append(self.opt.blank_symbol)
                else:
                    appendix.append(self.tmt_lines[tmt_i].strip())

            appendix_str = self.opt.concat_symbol.join(appendix)
            self.lock.acquire()
            self.cache[query] = appendix_str
            self.lock.release()
        else:
            appendix_str = self.cache[query]
            # print(query, self.cache)    # debug

        aug_query = f'{query.strip()}{self.opt.concat_symbol}{appendix_str}\n'
        self.lock.acquire()
        self.res_container[q_i] = (aug_query, query_target)
        # print(aug_query)     # debug
        self.lock.release()

    def nbest_process(self, q_i, query, query_target):
        cand_indices = match_fuzzy(query, self.search_index, self.opt)
        cand_indices = calc_edit_distance(query, cand_indices, self.tms_lines, self.opt)
        appendix = []
        for i in range(self.opt.format_n):
            try:
                tmt_i = cand_indices[i]
            except IndexError as e:
                # appendix.append(self.opt.blank_symbol)    # todo need to add blank token?
                break
            else:
                appendix.append(self.tmt_lines[tmt_i].strip())

        appendix = [f'{query.strip()}{self.opt.concat_symbol}{a}' for a in appendix]
        if len(appendix) == 0:
            return
        self.lock.acquire()
        self.res_container[q_i] = (appendix, query_target)
        self.lock.release()

    def run(self):
        while True:
            try:
                q_i, query, query_target = self.queue.get(
                    timeout=self.opt.subprocess_timeout)  # block=False may be dangerous within multi-threading
                # print(f'{self.p_name}, {self.queue.qsize()}')    # debug
            except queue.Empty as e:
                print(
                    f'Process [{self.p_name}] terminated for empty queue. Current queue length [{self.queue.qsize()}]')
                self.queue.join()
                break

            if self.opt.format_mode == 'series':
                self.concat_process(q_i, query, query_target)
            elif self.opt.format_mode == 'parallel':
                self.nbest_process(q_i, query, query_target)
            else:
                raise Exception(f'Invalid format mode {self.opt.format_mode}')

            self.queue.task_done()
            current_queue_size = self.queue.qsize()
            if current_queue_size % self.opt.report_every == 0 and current_queue_size > 0:
                print(f'{current_queue_size} pairs left', flush=True)


class WorkerPool():
    def __init__(self, queue, size, search_index, opt, tms_lines, tmt_lines, cache, res_container):
        self.queue = queue
        self.pool = []
        self.lock = Lock()
        for i in range(size):
            print(f'Starting subprocess[{i}]')
            self.pool.append(QueryWorker(i, self.queue, self.lock,
                                         search_index=search_index,
                                         opt=opt,
                                         tms_lines=tms_lines,
                                         tmt_lines=tmt_lines,
                                         cache=cache,
                                         res_container=res_container))

    def startWork(self):
        for p in self.pool:
            p.start()

    def joinAll(self):
        for p in self.pool:
            p.join()


def process(opt):
    print('Reading query data...')
    with open(opt.query, 'r') as f:
        query_lines = f.readlines()

    print('Reading query target data...')
    with open(opt.query_target, 'r') as f:
        qt_lines = f.readlines()

    print('Reading source side translation memory data...')
    with open(opt.translation_memory_src, 'r') as f:
        tms_lines = f.readlines()

    print('Reading target side translation memory data...')
    with open(opt.translation_memory_tgt, 'r') as f:
        tmt_lines = f.readlines()

    print('Building Search Index...')
    search_index = SI([set(l.strip().split()) for l in tms_lines],    # SSS requires each entry to be a set
                      similarity_threshold=opt.sss_lambda,
                      similarity_func_name='containment_min')    # paper indicates the func name is called containment_max

    print('Building Task Queue...')
    _queue = JoinableQueue()
    i = 0
    assert len(query_lines) == len(qt_lines)
    for q in tqdm(query_lines, mininterval=1.0, ncols=100, leave=True):
        query_target = qt_lines[i].strip()
        # considering the possible extension at target side in the future,it's saver to push target sents in cache too.
        _queue.put((i, q,
                    query_target))
        i += 1

    manager = Manager()
    cache = manager.dict()
    res_container = manager.dict()
    print('Initializing Workers Pool...')
    workers_pool = WorkerPool(_queue, opt.workers, search_index, opt, tms_lines, tmt_lines, cache, res_container)
    workers_pool.startWork()
    workers_pool.joinAll()

    print('Writing result file...')
    wf_src = open(f'{opt.query}.{opt.output_flag}', 'w')
    wf_tgt = open(f'{opt.query_target}.{opt.output_flag}', 'w')
    for q_i in tqdm(sorted(res_container), mininterval=0.5, ncols=50):
        aug_q, q_t = res_container[q_i]
        if type(aug_q) is list:
            for q in aug_q:
                wf_src.write(f'{q.strip()}\n')
                wf_tgt.write(f'{q_t}\n')
        else:
            wf_src.write(aug_q)
            wf_tgt.write(f'{q_t}\n')
    wf_src.close(), wf_tgt.close()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-q', '--query', required=True,
                        help='Path to the query file.')
    parser.add_argument('-qt', '--query-target', required=True,
                        help='Path to the target corpus corresponding to the query.')
    parser.add_argument('-tms', '--translation-memory-src', required=True,
                        help='Path to the source side translation memory file.')
    parser.add_argument('-tmt', '--translation-memory-tgt', required=True,
                        help='Path to the target side translation memory file.')

    parser.add_argument('--output-flag', default='nfr',
                        help='A suffix of output filename.')
    parser.add_argument('-sss-nbest', default=2000, type=int,
                        help='N Best similar sentences selected by SetSimilaritySearch.')
    parser.add_argument('-sss-lambda', default=0.5, type=float,
                        help='Threshold for SetSimilaritySearch')
    parser.add_argument('--include-perfect-match', action='store_true', default=False,
                        help='Perfect match will be included during sss.')
    parser.add_argument('--ed-lambda', default=0.5, type=float,
                        help='Threshold for edit distance score.')
    parser.add_argument('--format-mode', default='series',
                        help='Format mode. "series" and "parallel" are available.')
    parser.add_argument('--format-n', default=3, type=int,
                        help='Deciding format N.')

    parser.add_argument('--workers', default=16, type=int,
                        help='Multi-Processing.')
    parser.add_argument('--subprocess-timeout', default=60, type=int,
                        help='Timeout for a subprocess getting task from queue.')

    parser.add_argument('--concat-symbol', default=' @@@ ')
    parser.add_argument('--blank-symbol', default='[BLANK]')

    parser.add_argument('--report-every', default=100000, type=int,
                        help='Log interval.')

    opt = parser.parse_args()

    start_time = time.time()
    process(opt)
    end_time = time.time()
    print(f'Time Cosumed:{end_time - start_time}')


if __name__ == '__main__':
    main()
