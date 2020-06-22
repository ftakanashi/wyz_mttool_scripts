#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
# import numpy as np
import cupy as cp
import os
try:
    import cPickle as pickle
except ImportError as e:
    import pickle
import time
import queue

from multiprocessing import Process, Lock, Manager, JoinableQueue
from scipy.spatial.distance import cdist
from tqdm import tqdm

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def topk(array, k):
    a_i = cp.array(list(reversed(array.argpartition(-k)[-k:])), dtype=int)
    v = array[a_i]
    arg_i = list(reversed(v.argsort()))
    v = v[arg_i]
    a_i = a_i[arg_i]
    return v, a_i

class QueryWorker(Process):
    def __init__(self, p_name, queue, lock , **kwargs):
        super(QueryWorker, self).__init__()
        self.p_name = p_name
        self.queue = queue
        self.lock = lock

        self.opt = kwargs.get('opt')

        self.tms_embedding = kwargs.get('tms_embedding')
        self.tmt_embedding = kwargs.get('tmt_embedding')

        self.res_container = kwargs.get('res_container')
        self.cache = kwargs.get('cache')

    def run(self):
        while True:
            try:
                q_i, q_embedding = self.queue.get(
                    timeout=5
                )
            except queue.Empty as e:
                print(
                    f'Process [{self.p_name}] terminated for empty queue. Current queue length [{self.queue.qsize()}]')
                self.queue.join()
                break

            self.process_query(q_i, q_embedding)
            self.queue.task_done()

            q_size = self.queue.qsize()
            if q_size % self.opt.report_every == 0:
                print(f'From worker-{self.p_name}: {q_size} pairs left.', flush=True)

    def process_query(self, q_i, q_embedding):
        if type(q_embedding) is not list:
            q_embedding = [q_embedding, ]

        # if not q_embedding[0] not in self.cache:
        tms_score = 1 - cdist(q_embedding, self.tms_embedding, 'cosine')[0]
        if not self.opt.include_perfect_match:
            tms_score[tms_score>0.99] = -float('inf')

        tmt_score = 1 - cdist(q_embedding, self.tmt_embedding, 'cosine')[0]
        if not self.opt.include_perfect_match:
            tmt_score[tmt_score>0.99] = -float('inf')
            tmt_score[tms_score==-float('inf')] = -float('inf')

        top_tms_v, top_tms_i = topk(tms_score, self.opt.topk)
        top_tmt_v, top_tmt_i = topk(tmt_score, self.opt.topk)

        top_tms_i += self.opt.shard_i * self.opt.shard_max_len
        top_tmt_i += self.opt.shard_i * self.opt.shard_max_len

        top_v = cp.hstack([top_tms_v, top_tmt_v])
        top_i = cp.hstack([top_tms_i, top_tmt_i])

        arg_i = list(reversed(top_v.argsort()))
        top_v = top_v[arg_i][:self.opt.topk]
        top_i = top_i[arg_i][:self.opt.topk]
        #
        #     self.cache[q_embedding[0]] = (top_v, top_i)
        # else:
        #     top_v, top_i = self.cache[q_embedding[0]]

        self.lock.acquire()
        self.res_container[q_i] = (top_v, top_i)
        self.lock.release()

class WorkerPool():
    def __init__(self, queue, opt, cache, res_container, tms_embedding, tmt_embedding):
        self.queue = queue
        self.pool = []
        self.lock = Lock()
        for i in range(opt.workers):
            print(f'Starting subprocess[{i}]')
            self.pool.append(QueryWorker(i, self.queue, self.lock,
                                         opt=opt,
                                         cache=cache,
                                         res_container=res_container,
                                         tms_embedding=tms_embedding,
                                         tmt_embedding=tmt_embedding
                                         ))

    def startWork(self):
        for p in self.pool:
            p.start()

    def joinAll(self):
        for p in self.pool:
            p.join()


def process(opt):
    print('Reading in query embedding...')
    with open(opt.query_embedding, 'rb') as f:
        query_embedding = pickle.load(f)

    print('Reading in corpus embedding...')
    with open(opt.corpus_embedding, 'rb') as f:
        corpus_embedding = pickle.load(f)

    tms_embedding = corpus_embedding['tms']
    tmt_embedding = corpus_embedding['tmt']

    print('Building queue...')
    worker_queue = JoinableQueue()
    i = 0
    for q in tqdm(query_embedding, mininterval=0.5, ncols=50):
        worker_queue.put((i, q))
        i += 1

    print('Initializing workers pool...')
    manager = Manager()
    cache = manager.dict()
    res_container = manager.dict()

    worker_pool = WorkerPool(worker_queue, opt, cache, res_container, tms_embedding, tmt_embedding)
    worker_pool.startWork()
    worker_pool.joinAll()

    print('Writing result file...')
    fn = os.path.join(opt.output_dir, f'{opt.output_prefix}.{opt.shard_i}')
    wf = open(fn, 'w')
    for q_i in sorted(res_container):
        top_v, top_i = res_container[q_i]
        s = []
        for v, i in zip(top_v, top_i):
            s.append(f'{v} {i}')
        s = ' ||| '.join(s)

        wf.write(f'{s}\n')

    wf.close()

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('--query-embedding', required=True)
    parser.add_argument('--corpus-embedding', required=True)

    parser.add_argument('--topk', default=3, type=int,
                        help='DEFAULT: 3')
    parser.add_argument('--include-perfect-match', action='store_true', default=False)

    parser.add_argument('--shard-i', required=True, type=int)
    parser.add_argument('--shard-max-len', required=True, type=int)
    parser.add_argument('--workers', default=10, type=int,
                        help='DEFAULT: 10')
    parser.add_argument('--output-dir', default=os.path.join(BASE_DIR, 'splited'),
                        help=f'DEFAULT: {os.path.join(BASE_DIR, "splited")}')
    parser.add_argument('--output-prefix', default='match',
                        help='DEFAULT: match')

    parser.add_argument('--report-every', default=100000, type=int)


    opt = parser.parse_args()

    start = time.time()
    process(opt)
    end = time.time()

    print(f'Time Consumed: {end - start} secs...')

if __name__ == '__main__':
    main()