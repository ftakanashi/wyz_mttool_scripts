#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import os
try:
    import cPickle as pickle
except ImportError as e:
    import pickle

from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def dump(obj, fn):
    with open(fn, 'wb') as f:
        pickle.dump(obj, f)

def process(opt):

    sbert = SentenceTransformer(opt.sbert_model)
    bz = opt.build_batch_size

    if opt.query_input is not None:
        print('Building query emebdding...')
        with open(opt.query_input, 'r') as f:
            query_lines = [l.strip() for l in f.readlines()]

        query_embedding = sbert.encode(query_lines, show_progress_bar=True, batch_size=bz)
        if not opt.fp32:    # default use fp16
            query_embedding = [q.astype('float16') for q in query_embedding]
        dump(query_embedding, os.path.join(opt.cache_dir, 'query_embedding'))

    if opt.src_prefix is None or opt.tgt_prefix is None or opt.max_shard_num < 0:
        print('No corpus file specified. End processing.')
        return

    # check file existence
    for i in range(opt.max_shard_num):
        if not os.path.isfile(os.path.join(opt.splited_dir, f'{opt.src_prefix}.{i}')):
            raise FileNotFoundError(f'{opt.src_prefix}.{i}')
        if not os.path.isfile(os.path.join(opt.splited_dir, f'{opt.tgt_prefix}.{i}')):
            raise FileNotFoundError(f'{opt.tgt_prefix}.{i}')

    for i in range(opt.max_shard_num):
        tms_fn = os.path.join(opt.splited_dir, f'{opt.src_prefix}.{i}')
        tmt_fn = os.path.join(opt.splited_dir, f'{opt.tgt_prefix}.{i}')
        print(f'Building tms & tmt embedding for {tms_fn} and {tmt_fn}')
        d = {}
        with open(tms_fn, 'r') as f: tms_lines = [l.strip() for l in f.readlines()]
        with open(tmt_fn, 'r') as f: tmt_lines = [l.strip() for l in f.readlines()]

        tms_embedding = sbert.encode(tms_lines, show_progress_bar=True, batch_size=bz)
        tmt_embedding = sbert.encode(tmt_lines, show_progress_bar=True, batch_size=bz)

        if not opt.fp32:    # default use fp16
            tms_embedding = [t.astype('float16') for t in tms_embedding]
            tmt_embedding = [t.astype('float16') for t in tmt_embedding]

        d['tms'] = tms_embedding
        d['tmt'] = tmt_embedding

        dump(d, os.path.join(opt.cache_dir, f'corpus_embedding.{i}'))


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('-n', '--max-shard-num', default=-1, type=int)
    parser.add_argument('-s', '--src-prefix', default=None)
    parser.add_argument('-t', '--tgt-prefix', default=None)
    parser.add_argument('--splited-dir', default=os.path.join(BASE_DIR, 'splited'))
    parser.add_argument('--query-input', default=None)
    parser.add_argument('--sbert-model', default=os.path.join(BASE_DIR, 'sbert-model'))
    parser.add_argument('--cache-dir', default=os.path.join(BASE_DIR, 'cache'))

    parser.add_argument('--build-batch-size', type=int, default=256)

    parser.add_argument('--fp32', action='store_true', default=False)

    opt = parser.parse_args()

    process(opt)

if __name__ == '__main__':
    main()