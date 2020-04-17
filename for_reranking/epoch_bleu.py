#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--src', required=True, help='Source language.')
    parser.add_argument('-t', '--tgt', required=True, help='Target language.')

    parser.add_argument('--range', required=True, help='A range like 20-40')
    parser.add_argument('--checkpoint-dir', required=True, help='Path to the dir where checkpoints are saved.')

    parser.add_argument('--fairseq-dir', default='fairseq')
    parser.add_argument('--data-bin-dir', default='data-bin')
    parser.add_argument('--max-tokens', type=int, default=1024)

    opt = parser.parse_args()

    cpt_range = [int(i) for i in opt.range.split('-')]
    cpt_range = range(cpt_range[0], cpt_range[1]+1)

    data_bin_dir = f'{opt.data_bin_dir}.{opt.src}2{opt.tgt}'
    for epoch_num in cpt_range:
        os.system(f'python {opt.fairseq_dir}/generate.py {data_bin_dir} --path {opt.checkpoint_dir}/checkpoint{epoch_num}.pt'
                  f' --max-tokens {opt.max_tokens} --quiet | tee -a generate.log')

if __name__ == '__main__':
    main()