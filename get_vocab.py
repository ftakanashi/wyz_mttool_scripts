#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
此脚本用于提取某些语料文件涵盖的词汇表
期待语料文件应该已经完成了基本的tokenization，并且以空格作为分隔符。
'''

import argparse
import collections
import os
import string

from tqdm import tqdm

def get_vocab(opt):
    src_files = opt.input.split(',')
    sep = opt.seperator

    for src_file in src_files:
        if not os.path.isfile(src_file):
            raise Exception('File [{}] doesn\'t exist.'.format(src_file))

    c = collections.Counter()
    for src_file in src_files:
        print('Processing [{}]...'.format(src_file))
        with open(src_file, 'r', encoding=opt.encoding) as f:
            for line in tqdm(f, mininterval=0.5):
                for w in line.split(sep):
                    c[w] += 1
    with_freq = opt.with_freq
    min_freq = opt.min_freq
    with open(opt.output, 'w', encoding=opt.encoding) as f:
        for word, freq in sorted(c.items(), key=lambda x:x[1], reverse=True):
            word = word.strip()
            # 最小词频
            if freq < min_freq or word in string.whitespace:
                continue
            # 是否写入词频
            if with_freq:
                txt = '{}\t{}'.format(word, freq)
            else:
                txt = word

            f.write('{}\n'.format(txt))

def main():

    parser = argparse.ArgumentParser(description='Extract vocabulary from (multiple) corpus file(s). Write vocab into an output file.')

    parser.add_argument('-i', '--input', type=str, required=True,
                        help='Specify the input file(s). Use English comma to seperate diffrent files if there are many of them.')

    parser.add_argument('-o', '--output', type=str, required=True,
                        help='Specify the output file.')

    parser.add_argument('--encoding', type=str, default='utf-8',
                        help='Specify the encoding format of non-ascii files.')

    parser.add_argument('--min_freq', type=int, default=5,
                        help='Ignore words whose frequency is less than the specified one.')

    parser.add_argument('--seperator', type=str, default=' ',
                        help='Specify the seperator to seperate tokens in corpus.')

    parser.add_argument('--with_freq', action='store_true',
                        help='Write the output file with frequency of word.')

    opt = parser.parse_args()

    get_vocab(opt)


if __name__ == '__main__':
    main()