#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import cupy as cp
import os

try:
    import cPickle as pickle
except ImportError as e:
    import pickle
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def cdist(a, b):
    norm = cp.linalg.norm
    t = a.dot(b.transpose())
    a_norm = norm(a, axis=1).reshape(-1, 1)
    t = t / a_norm
    del a_norm
    b_norm = norm(b, axis=1).reshape(-1, 1)
    t = t.transpose()
    t = t / b_norm
    del b_norm
    t = t.transpose()
    return t


def topk(array, k):
    assert array.ndim == 2
    top_i = array.astype('float32').argpartition(-k)[:,
            -k:]  # cupy.argpartition do whole sorting for implementation reason
    top_i = cp.flip(top_i, axis=1)
    top_v = cp.vstack([array[r, top_i[r]] for r in range(array.shape[0])])
    return top_v, top_i


def match_fuzzy(q, tms, tmt, opt):
    tms_score = cdist(q, tms)
    if not opt.include_perfect_match:
        tms_score[tms_score > 0.99] = -float('inf')

    tmt_score = cdist(q, tmt)
    if not opt.include_perfect_match:
        tmt_score[tms_score == -float('inf')] = -float('inf')
        tmt_score[tmt_score > 0.99] = -float('inf')

    tms_top_v, tms_top_i = topk(tms_score, opt.topk)
    tmt_top_v, tmt_top_i = topk(tmt_score, opt.topk)

    tms_top_i += opt.shard_i * opt.shard_max_len
    tmt_top_i += opt.shard_i * opt.shard_max_len

    top_v = cp.hstack([tms_top_v, tmt_top_v])
    top_i = cp.hstack([tms_top_i, tmt_top_i])

    arg_i = cp.flip(top_v.astype('float32').argsort(axis=1), axis=1)
    top_v = top_v[cp.arange(top_v.shape[0]).reshape(-1, 1), arg_i][:, :opt.topk]
    top_i = top_i[cp.arange(top_i.shape[0]).reshape(-1, 1), arg_i][:, :opt.topk]

    return top_v, top_i


def process(opt):
    print('Reading in query embedding...')
    with open(opt.query_embedding, 'rb') as f:
        query_embedding = pickle.load(f)

    print('Reading in corpus embedding...')
    with open(opt.corpus_embedding, 'rb') as f:
        corpus_embedding = pickle.load(f)

    tms_embedding = cp.asarray([cp.asarray(v) for v in corpus_embedding['tms']])
    tmt_embedding = cp.asarray([cp.asarray(v) for v in corpus_embedding['tmt']])

    batch_i = 0
    wf_fn = os.path.join(opt.output_dir, f'{opt.output_prefix}.{opt.shard_i}')
    wf = open(wf_fn, 'w')
    while batch_i < len(query_embedding):
        batch_query_embedding = cp.asarray(query_embedding[batch_i:batch_i + opt.batch_size])
        top_v, top_i = match_fuzzy(batch_query_embedding, tms_embedding, tmt_embedding, opt)
        batch_i += opt.batch_size

        if batch_i % opt.report_every == 0:
            print(f'{batch_i} pairs done...')

        for v, i in zip(top_v, top_i):
            wf.write(' ||| '.join([f'{v[_i]} {i[_i]}' for _i in range(opt.topk)]) + '\n')


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--query-embedding', required=True)
    parser.add_argument('--corpus-embedding', required=True)

    parser.add_argument('--batch-size', default=500, type=int,
                        help='DEFAULT: 500')
    parser.add_argument('--topk', default=3, type=int,
                        help='DEFAULT: 3')
    parser.add_argument('--include-perfect-match', action='store_true', default=False)

    parser.add_argument('--shard-i', required=True, type=int)
    parser.add_argument('--shard-max-len', required=True, type=int)
    parser.add_argument('--output-dir', default=os.path.join(BASE_DIR, 'splited'),
                        help=f'DEFAULT: {os.path.join(BASE_DIR, "splited")}')
    parser.add_argument('--output-prefix', default='match',
                        help='DEFAULT: match')

    parser.add_argument('--report-every', default=100000, type=int,
                        help='DEFAULT: 100000')

    opt = parser.parse_args()

    start = time.time()
    process(opt)
    end = time.time()

    print(f'Time Consumed: {end - start} secs...')


if __name__ == '__main__':
    main()
