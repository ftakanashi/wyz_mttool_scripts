#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import numpy as np
from sentence_transformers import SentenceTransformer

def process(opt):
    print('Reading data...')
    with open(opt.src, 'r') as f:
        src_lines = [l.strip() for l in f]

    with open(opt.tgt, 'r') as f:
        tgt_lines = [l.strip() for l in f]

    print('Loading S-BERT...')
    sbert = SentenceTransformer(opt.model_dir)

    print('Calculating embedding...')
    src_embedding = sbert.encode(src_lines, show_progress_bar=True, batch_size=opt.batch_size)
    tgt_embedding = sbert.encode(tgt_lines, show_progress_bar=True, batch_size=opt.batch_size)

    print('Writing embeddings to file...')
    np.hstack(src_embedding).flatten().tofile(opt.src_output)
    np.hstack(tgt_embedding).flatten().tofile(opt.tgt_output)

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--src', required=True)
    parser.add_argument('-t', '--tgt', required=True)
    parser.add_argument('-so', '--src-output', required=True)
    parser.add_argument('-to', '--tgt-output', required=True)

    parser.add_argument('--model-dir', default='sbert-model',
                        help='DEFAULT: "sbert-model"')
    parser.add_argument('--batch-size', default=128, type=int,
                        help='DEFAULT: 128')

    opt = parser.parse_args()

    process(opt)

if __name__ == '__main__':
    main()