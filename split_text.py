#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import os
import random
import sys

VER = sys.version[0]

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--src',
                        help='Path to source language corpus.')

    parser.add_argument('-g', '--trg',
                        help='Path to target language corpus.')

    parser.add_argument('-e', '--encoding', default='utf-8',
                        help='Specify the encoding format.')

    parser.add_argument('-t', '--train', type=float, default=0.9,
                        help='Rate of train corpus. Default: 0.9')

    parser.add_argument('-v', '--valid', type=float, default=0.05,
                        help='Rate of valid corpus. Default: 0.05')

    parser.add_argument('-x', '--test', type=float, default=0.05,
                        help='Rate of test corpus. Default: 0.05')

    opt = parser.parse_args()

    if not os.path.isfile(opt.src) or not os.path.isfile(opt.trg):
        raise Exception('File or Target Directory not Found')

    if opt.train + opt.valid + opt.test != 1.0:
        raise ValueError('Sum of train, valid & test must equal to 1.0')

    with open(opt.src, 'r') as f:
        src_contents = f.readlines()
    with open(opt.trg, 'r') as f:
        trg_contents = f.readlines()

    if len(src_contents) != len(trg_contents):
        raise Exception('Length of Source and Target File do not match. Source Lines: {},  Target Lines: {}'.format(len(src_contents), len(trg_contents)))

    max_len = len(src_contents)
    indices = list(range(max_len))
    random.shuffle(indices)

    train_ms = int(max_len * opt.train)
    valid_ms = int(train_ms + max_len * opt.valid)

    train_indices = indices[:train_ms]
    valid_indices = indices[train_ms:valid_ms]
    test_indices = indices[valid_ms:]

    src_dir = os.path.dirname(os.path.abspath(opt.src))
    src_prefix = os.path.basename(opt.src)
    src_train = open(os.path.join(src_dir, '{}.train'.format(src_prefix)), 'w')
    src_valid = open(os.path.join(src_dir, '{}.valid'.format(src_prefix)), 'w')
    src_test = open(os.path.join(src_dir, '{}.test'.format(src_prefix)), 'w')
    
    trg_dir = os.path.dirname(os.path.abspath(opt.trg))
    trg_prefix = os.path.basename(opt.trg)
    trg_train = open(os.path.join(trg_dir, '{}.train'.format(trg_prefix)), 'w')
    trg_valid = open(os.path.join(trg_dir, '{}.valid'.format(trg_prefix)), 'w')
    trg_test = open(os.path.join(trg_dir, '{}.test'.format(trg_prefix)), 'w')
    
    for idx in train_indices:
        src_train.write(src_contents[idx])
        trg_train.write(trg_contents[idx])
        
    for idx in valid_indices:
        src_valid.write(src_contents[idx])
        trg_valid.write(trg_contents[idx])
        
    for idx in test_indices:
        src_test.write(src_contents[idx])
        trg_test.write(trg_contents[idx])
        
    for f in (src_train, src_valid, src_test, trg_train, trg_valid, trg_test):
        f.close()


if __name__ == '__main__':
    main()

