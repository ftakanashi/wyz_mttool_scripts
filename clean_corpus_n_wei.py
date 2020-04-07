#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
from tqdm import tqdm

EPS = 1e-6

def process_line(opt, src_line, tgt_line):
    src_tokens = src_line.strip().split()
    tgt_tokens = tgt_line.strip().split()

    if len(src_tokens) > opt.max_length or len(tgt_tokens) > opt.max_length:
        return False

    st_ratio = len(src_tokens) / (float(len(tgt_tokens)) + EPS)
    ts_ratio = 1 / st_ratio

    if st_ratio > opt.ratio or ts_ratio > opt.ratio:
        return False

    return True

def filter_main(opt):
    src_fn = f'{opt.prefix}.{opt.src}'
    tgt_fn = f'{opt.prefix}.{opt.tgt}'

    with open(src_fn, 'r') as f:
        src_lines = f.readlines()
    with open(tgt_fn, 'r') as f:
        tgt_lines = f.readlines()

    res_container = []
    trash_container = []

    i = 0
    for src_line in tqdm(src_lines, mininterval=0.5, ncols=50):
        tgt_line = tgt_lines[i]
        if process_line(opt, src_line, tgt_line):
            res_container.append((src_line, tgt_line))
        else:
            if opt.collect_trash:
                trash_container.append((src_line, tgt_line))

        i += 1

    return res_container, trash_container

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--src', required=True,
                        help='Source language.')
    parser.add_argument('-t', '--tgt', required=True,
                        help='Target language.')
    parser.add_argument('-p', '--prefix', required=True,
                        help='Prefix of corpus file.')

    parser.add_argument('-r', '--ratio', type=float, default=1.8,
                        help='Specify the maximum length ratio in both s-t and t-s direction.')
    parser.add_argument('-m', '--max-length', type=int, default=512,
                        help='Specify the maximum length of sequence.')

    parser.add_argument('--collect-trash', action='store_true', default=False,
                        help='Collect pairs that were filtered out.')

    opt = parser.parse_args()

    res, trash = filter_main(opt)

    cleaned_src_fn = f'{opt.prefix}.clean.{opt.src}'
    cleaned_tgt_fn = f'{opt.prefix}.clean.{opt.tgt}'
    src_fw = open(cleaned_src_fn, 'w')
    tgt_fw = open(cleaned_tgt_fn, 'w')

    for s,t in res:
        print('Writing in cleaned files...')
        src_fw.write(f'{s.strip()}\n')
        tgt_fw.write(f'{t.strip()}\n')

    src_fw.close(), tgt_fw.close()

    if opt.collect_trash:
        src_fw = open(f'{opt.prefix}.trash.{opt.src}', 'w')
        tgt_fw = open(f'{opt.prefix}.trash.{opt.tgt}', 'w')
        for s,t in trash:
            print('Writing in trash files...')
            src_fw.write(f'{s.strip()}\n')
            tgt_fw.write(f'{t.strip()}\n')

        src_fw.close(),tgt_fw.close()

if __name__ == '__main__':
    main()