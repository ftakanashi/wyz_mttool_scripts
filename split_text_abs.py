#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
Split a whole bunch of text data into train/valid/test dataset.
Outputing files like train.src|tgt valid.src|tgt test.src|tgt
'''

import argparse
import codecs
import os
import random

from tqdm import tqdm

BASE_DIR = os.getcwd()

def check_opt(opt):
    print('Checking Arguments...')
    if not os.path.isfile(opt.source):
        raise Exception('Source Corpus File Not Exist.')

    if not os.path.isfile(opt.target):
        raise Exception('Target Corpus File Not Exist.')

    if '-' not in opt.language_pair:
        raise Exception('Invalid format of language pair expression.\ne.g. en-zh might be a correct format for'
                        'Chinese-English Translation')

    if not os.path.isdir(opt.destdir):
        raise Exception('Output Directory Not Exist.')

    if opt.figure_format not in ('abs', 'ratio'):
        raise Exception('Invalid figure format [{}]'.format(opt.figure_format))

    if opt.figure_format is 'abs':
        _ = int(opt.valid), int(opt.test), int(opt.train)
    else:
        valid_fig = float(opt.valid)
        test_fig = float(opt.test)
        train_fig = float(opt.train)
        if train_fig > 0:
            total_fig = valid_fig + test_fig + train_fig
        else:
            total_fig = valid_fig + test_fig

        if total_fig > 1:
            raise Exception('Invalid distribution for sets.')


def calc_lines(opt, total_len):
    print('Calculating line distribution...')
    if opt.figure_format is 'abs':
        train, valid, test = int(opt.train), int(opt.valid), int(opt.test)
        if train == -1:
            train = total_len - valid - test
        assert sum((train, valid, test)) <= total_len
    else:
        train_r, valid_r, test_r = float(opt.train), float(opt.valid), float(opt.test)
        if train_r == -1:
            train_r = 1.0 - valid_r - test_r
        assert sum((train_r, valid_r, test_r)) == 1.0

        train = int(total_len * train_r)
        valid = int(total_len * valid_r)
        test = int(total_len * test_r)

    return train, valid, test


def split_text(opt):
    print('Spliting data...')
    open = codecs.open
    src_f = open(opt.source, 'r', encoding=opt.encoding)
    tgt_f = open(opt.target, 'r', encoding=opt.encoding)

    src_content = src_f.readlines()
    tgt_content = tgt_f.readlines()

    src_f.close(), tgt_f.close()

    assert len(src_content) == len(tgt_content)
    total_len = len(src_content)
    indices = list(range(total_len))

    if opt.shuffle:
        random.shuffle(indices)

    src_suf, tgt_suf = opt.language_pair.split('-')

    train_num, valid_num, test_num = calc_lines(opt, total_len)
    train_indices = indices[:train_num]
    valid_indices = indices[train_num:valid_num+train_num]
    test_indices = indices[valid_num+train_num:test_num+valid_num+train_num]

    train_src = open(os.path.join(opt.destdir, 'train.{}'.format(src_suf)), 'w', encoding=opt.encoding)
    valid_src = open(os.path.join(opt.destdir, 'valid.{}'.format(src_suf)), 'w', encoding=opt.encoding)
    test_src = open(os.path.join(opt.destdir, 'test.{}'.format(src_suf)), 'w', encoding=opt.encoding)

    train_tgt = open(os.path.join(opt.destdir, 'train.{}'.format(tgt_suf)), 'w', encoding=opt.encoding)
    valid_tgt = open(os.path.join(opt.destdir, 'valid.{}'.format(tgt_suf)), 'w', encoding=opt.encoding)
    test_tgt = open(os.path.join(opt.destdir, 'test.{}'.format(tgt_suf)), 'w', encoding=opt.encoding)

    for i in tqdm(train_indices, mininterval=0.5, ncols=50, desc='Writing train set'):
        train_src.write(src_content[i])
        train_tgt.write(tgt_content[i])

    for i in tqdm(valid_indices, mininterval=0.5, ncols=50, desc='Writing valid set'):
        valid_src.write(src_content[i])
        valid_tgt.write(tgt_content[i])

    for i in tqdm(test_indices, mininterval=0.5, ncols=50, desc='Writing test set'):
        test_src.write(src_content[i])
        test_tgt.write(tgt_content[i])

    for f in (train_src, valid_src, test_src, train_tgt, valid_tgt, test_tgt):
        f.close()



def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--source', required=True,
                        help='Path to the source language corpus file.')
    parser.add_argument('-t', '--target', required=True,
                        help='Path to the target language corpus file.')
    parser.add_argument('-l', '--language-pair', required=True,
                        help='Specify the language pair in format like: en-zh')
    parser.add_argument('-d', '--destdir', default=BASE_DIR,
                        help='Directory to save the output files. DEFAULT: current directory.')
    parser.add_argument('-e', '--encoding', default='utf-8',
                        help='Specify the codecs to read/write file. DEFAULT: utf-8')

    parser.add_argument('--figure-format', default='abs',
                        help='Specify the figure format. Options are "abs" and "ratio". DEFAULT: abs')
    parser.add_argument('--shuffle', action='store_true',
                        help='Shuffle the rows before split the data.')
    parser.add_argument('--valid', required=True,
                        help='NUMBER or RATIO of rows for valid set.')
    parser.add_argument('--test', required=True,
                        help='NUMBER or RATIO of rows for test set.')
    parser.add_argument('--train', default=-1,
                        help='NUMBER or RATIO of rows for train set. DEFAULT: all rows not in valid and test.')

    opt = parser.parse_args()
    check_opt(opt)

    split_text(opt)


if __name__ == '__main__':
    main()