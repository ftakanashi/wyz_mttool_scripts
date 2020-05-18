#!/usr/bin/env python
# -*- coding:utf-8 -*-

from sentence_transformers import SentenceTransformer

import argparse
import numpy as np
import os
import queue
import torch

from multiprocessing import Process, Lock, JoinableQueue, Manager
from scipy.spatial.distance import cdist
from tqdm import tqdm


def cosine_similarity(a, b):
    return (a.dot(b)) / (np.linalg.norm(a) * np.linalg.norm(b))


def match_fuzzy(q_embedding, opt, tmt_lines, tms_embedding, tmt_embedding):
    score = torch.from_numpy(1 - cdist(q_embedding, tms_embedding, 'cosine')[0])
    src_topk_v, src_topk_i = score.topk(opt.format_n)

    score = torch.from_numpy(1 - cdist(q_embedding, tmt_embedding, 'cosine')[0])
    tgt_topk_v, tgt_topk_i = score.topk(opt.format_n)

    topk_v = torch.cat([src_topk_v, tgt_topk_v])
    topk_i = torch.cat([src_topk_i, tgt_topk_i])
    pushed_i, res = [], []
    for j in range(topk_v.size(0)):
        if topk_i[j] not in pushed_i and topk_v[j] >= opt.cosine_lambda:
            res.append(tmt_lines[topk_i[j]])
            pushed_i.append(topk_i[j])

    while len(res) < opt.format_n:
        res.append(opt.blank_symbol)
    return res[:opt.format_n]


class QueryWorker(Process):
    def __init__(self, p_name, queue, lock, **kwargs):
        super(QueryWorker, self).__init__()

        self.p_name = p_name
        self.queue = queue
        self.lock = lock

        self.opt = kwargs.get('opt')
        self.cache = kwargs.get('cache')
        self.mutual_data = kwargs.get('mutual_data')
        self.res_container = kwargs.get('res_container')

    def run(self):
        while True:
            try:
                q_i, query, query_target = self.queue.get(
                    timeout=self.opt.subprocess_timeout
                )
            except queue.Empty as e:
                print(
                    f'Process [{self.p_name}] terminated for empty queue. Current queue length [{self.queue.qsize()}]')
                self.queue.join()
                break

            self.concat_process(q_i, query, query_target)

            self.queue.task_done()
            current_queue_size = self.queue.qsize()
            if current_queue_size % self.opt.report_every == 0 and current_queue_size > 0:
                print(f'{current_queue_size} pairs left', flush=True)

    def concat_process(self, q_i, query, query_target):
        if query not in self.cache:
            sbert = self.mutual_data.get('sbert')
            q_embedding = sbert.encode([query])
            tmt_lines = self.mutual_data.get('tmt_lines')
            tms_embedding = self.mutual_data.get('tms_embedding')
            tmt_embedding = self.mutual_data.get('tmt_embedding')
            fuzzy_matches = match_fuzzy(q_embedding, self.opt, tmt_lines, tms_embedding, tmt_embedding)
            appendix_str = self.opt.concat_symbol.join(fuzzy_matches)

            self.lock.acquire()
            self.cache[query] = appendix_str
            self.lock.release()
        else:
            appendix_str = self.cache[query]

        aug_query = f'{query.strip()}{self.opt.concat_symbol}{appendix_str}\n'
        self.lock.acquire()
        self.res_container[q_i] = (aug_query, query_target)
        self.lock.release()


class WorkerPool():
    def __init__(self, queue, size, opt, cache, mutual_data, res_container):
        self.queue = queue
        self.pool = []
        self.lock = Lock()
        for i in range(size):
            print(f'Starting subprocess[{i}]')
            self.pool.append(QueryWorker(i, self.queue, self.lock,
                                         opt=opt,
                                         cache=cache,
                                         mutual_data=mutual_data,
                                         res_container=res_container))

    def startWork(self):
        for p in self.pool:
            p.start()

    def joinAll(self):
        for p in self.pool:
            p.join()


def process(opt):
    os.makedirs(opt.cache_dir, exist_ok=True)

    print('Reading in query and query target...')
    with open(opt.query, 'r') as f:
        query_lines = [l.strip() for l in f.readlines()]
    with open(opt.query_target, 'r') as f:
        qt_lines = [l.strip() for l in f.readlines()]

    print('Loading pretrained SBERT...')
    if opt.pretrained_model_path == '' or not os.path.isdir(opt.pretrained_model_path):
        opt.pretrained_model_path = 'distiluse-base-multilingual-cased'  # download or load model in cache
    embedder = SentenceTransformer(opt.pretrained_model_path)

    print('Building corpus embedding...')
    corpus_embedding_fn = os.path.join(opt.cache_dir, 'corpus_embedding')
    if os.path.isfile(corpus_embedding_fn):    # cache exists
        print(f'Found translation memory cache file in {corpus_embedding_fn}')
        corpus_embedding_info = torch.load(corpus_embedding_fn)
        tms_embedding = corpus_embedding_info['tms_embedding']
        tmt_embedding = corpus_embedding_info['tmt_embedding']
        tms_lines = corpus_embedding_info['tms_lines']
        tmt_lines = corpus_embedding_info['tmt_lines']
    else:
        print('Reading in tms and tmt...')
        with open(opt.translation_memory_src, 'r') as f:
            tms_lines = [l.strip() for l in f.readlines()]
        with open(opt.translation_memory_tgt, 'r') as f:
            tmt_lines = [l.strip() for l in f.readlines()]

        print('Building tms embedding...')
        tms_embedding = embedder.encode(tms_lines, show_progress_bar=True, batch_size=128)  # Using GPU
        print('Buliding tmt embedding...')
        tmt_embedding = embedder.encode(tmt_lines, show_progress_bar=True, batch_size=128)

        print('Writing into cache...')
        corpus_embedding_info = {'tms_lines': tms_lines,
                                 'tmt_lines': tmt_lines,
                                 'tms_embedding': tms_embedding,
                                 'tmt_embedding': tmt_embedding}
        torch.save(corpus_embedding_info, corpus_embedding_fn)

    print('Building workers queue...')
    _queue = JoinableQueue()
    i = 0
    assert len(query_lines) == len(qt_lines)
    for q in tqdm(query_lines, mininterval=1.0, ncols=100, leave=True):
        query_target = qt_lines[i].strip()
        # considering the possible extension at target side in the future,it's saver to push target sents in cache too.
        _queue.put((i, q, query_target))
        i += 1

    print('Initialzing worker pool...')
    manager = Manager()
    # some shared memory objects
    cache = manager.dict()
    res_container = manager.dict()
    mutual_data = manager.dict()
    mutual_data['sbert'] = embedder
    mutual_data['tms_embedding'] = tms_embedding
    mutual_data['tmt_embedding'] = tmt_embedding
    mutual_data['tmt_lines'] = tmt_lines

    workers_pool = WorkerPool(_queue, opt.workers, opt, cache, mutual_data, res_container)
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

    parser.add_argument('--pretrained-model-path', default='sbert-model',
                        help='Specify the path to the model file.')
    parser.add_argument('--cache-dir', default='cache',
                        help='Cache directory for caching things like the corpus embedding.')

    parser.add_argument('--workers', default=16, type=int,
                        help='Number of multi-processes.')
    parser.add_argument('--report-every', default=10000, type=int,
                        help='Log interval.')
    parser.add_argument('--subprocess-timeout', default=10, type=int,
                        help='Timeout for getting a task from queue.')

    parser.add_argument('--format-n', default=3, type=int,
                        help='nbest fuzzy matches.')
    parser.add_argument('--cosine-lambda', default=0.5, type=float,
                        help='A threshold for retrieving fuzzy matches.')

    parser.add_argument('--output-flag', default='sbert')
    parser.add_argument('--concat-symbol', default=' @@@ ')
    parser.add_argument('--blank-symbol', default='[BLANK]')

    opt = parser.parse_args()

    process(opt)


if __name__ == '__main__':
    main()
