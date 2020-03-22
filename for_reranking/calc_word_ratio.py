#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--src', required=True,
                        help='Path to the source corpus file.')
    parser.add_argument('--tgt', required=True,
                        help='Path to the target corpus file.')
    parser.add_argument('--std-ratio', default=0.0,
                        help='Will output deviation compared to the standard ratio if is specified.')
    parser.add_argument('-o', '--output', required=True,
                        help='Path to the output file.')

    opt = parser.parse_args()

    print('Reading source corpus...')
    with open(opt.src, 'r') as f:
        src_lines = f.readlines()

    print('Reading target corpus...')
    with open(opt.tgt, 'r') as f:
        tgt_lines = f.readlines()

    fw = open(opt.output, 'w')

    std_ratio = float(opt.std_ratio)
    for i, src in enumerate(src_lines):
        tgt = tgt_lines[i]
        src_len = len(src.strip().split())
        tgt_len = len(tgt.strip().split())
        ratio = float(src_len) / tgt_len
        if std_ratio == 0.0:
            fw.write('{}\n'.format(ratio))
        else:
            deviation = abs(( ratio - std_ratio ) / std_ratio)
            fw.write('{}\n'.format(-deviation))

    fw.close()

if __name__ == '__main__':
    main()
