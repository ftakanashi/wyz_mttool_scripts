#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
Tokenize Chinese corpus based on jieba tokenizer.
'''

import argparse
import jieba
import os
import sys

from tqdm import tqdm

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str,
                        help='Path your input file. Expected to be a untokenized Chinese corpus.')
    parser.add_argument('-o', '--output', type=str,
                        help='Path your output file.')
    parser.add_argument('-e', '--encoding', default='utf-8')

    parser.add_argument('--no-progressbar', default=False, action='store_true',
                        help='Do not show the progress bar.')

    opt = parser.parse_args()

    if not os.path.isfile(opt.input):
        raise Exception('File not Found')

    if sys.version[0] == '3':
        with open(opt.input, 'r', encoding=opt.encoding) as rf:
            with open(opt.output, 'w', encoding=opt.encoding) as wf:
                if opt.no_progressbar:
                    itr = rf
                else:
                    rf_lines = rf.readlines()
                    itr = tqdm(rf_lines, mininterval=0.5, ncols=100)
                for line in itr:
                    splited_line = ' '.join(list(jieba.cut(line)))
                    wf.write(splited_line)

    elif sys.version[0] == '2':
        with open(opt.input, 'r') as rf:
            with open(opt.output, 'w') as wf:
                if opt.no_progressbar:
                    itr = rf
                else:
                    rf_lines = rf.readlines()
                    itr = tqdm(rf_lines, mininterval=0.5, ncols=100)
                for line in itr:
                    line = line.decode('utf-8')
                    splited_line = ' '.join(list(jieba.cut(line))).encode(opt.encoding)
                    wf.write(splited_line)

if __name__ == '__main__':
    main()
