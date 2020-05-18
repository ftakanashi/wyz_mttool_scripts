#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
remove all the duplicated sentences in specified corpus file.
'''

import argparse
import sys

def my_print(msg, end='\n'):
    sys.stderr.write(msg + end)

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--src', required=True,
                        help='Source Language')
    parser.add_argument('-t', '--tgt', required=True,
                        help='Target Language')
    parser.add_argument('-p', '--prefix', required=True,
                        help='Prefix of corpus file.')
    parser.add_argument('--output-flag', default='rm',
                        help='A symbol in output filename.')

    opt = parser.parse_args()
    prefix = opt.prefix
    symbol = opt.output_flag

    my_print('Reading Source data...')
    with open(f'{prefix}.{opt.src}', 'r') as f:
        src_lines = f.readlines()

    my_print('Reading Target data...')
    with open(f'{prefix}.{opt.tgt}', 'r') as f:
        tgt_lines = f.readlines()

    assert len(src_lines) == len(tgt_lines)

    pairs = []
    my_print('Collecting pairs...')
    for i, src_line in enumerate(src_lines):
        tgt_line = tgt_lines[i].strip()
        src_line = src_line.strip()
        pairs.append(f'{src_line} ||| {tgt_line}')

    my_print('Removing duplicate ones...')
    origin_count = len(pairs)
    pairs = list(set(pairs))
    removed_count = len(pairs)
    my_print(f'{origin_count - removed_count} pairs are removed...')

    my_print('Writing new files...')
    src_wf = open(f'{prefix}.{symbol}.{opt.src}', 'w')
    tgt_wf = open(f'{prefix}.{symbol}.{opt.tgt}', 'w')
    for p in pairs:
        src_line, tgt_line = p.split('|||')
        src_line, tgt_line = src_line.strip(), tgt_line.strip()
        src_wf.write(src_line + '\n')
        tgt_wf.write(tgt_line + '\n')

    src_wf.close(), tgt_wf.close()

if __name__ == '__main__':
    main()