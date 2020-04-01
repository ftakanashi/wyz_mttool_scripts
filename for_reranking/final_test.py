#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run(cmd):
    print(cmd)
    os.system(cmd)

def calc_score(opt):

    SRC = opt.src
    TGT = opt.tgt
    N = opt.repeat_number

    TMP = os.path.join(BASE_DIR, 'reranking_tmp')
    os.makedirs(TMP, exist_ok=True)

    run('python ')

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--src', required=True,
                        help='Source Language')
    parser.add_argument('-t', '--tgt', required=True,
                        help='Target Language')
    parser.add_argument('-n', '--repeat-number', required=True, type=int,
                        help='Repeat Number')
    parser.add_argument('-r', '--source-ref', required=True,
                        help='Path to the source corpus file.(Used to expand data in row if n>1)')
    parser.add_argument('-p', '--hyp', required=True,
                        help='Path to the hypothesis file.')

    parser.add_argument('--model-dir', default=os.path.join(BASE_DIR, 'model'),
                        help='Path to the model dir')
    parser.add_argument('--tool-script-dir', default=os.path.join(BASE_DIR, 'wyz_mttool_scripts'),
                        help='Path to the tool script dir')
    parser.add_argument('--data-dir', default=os.path.join(BASE_DIR, 'data'))
    parser.add_argument('--data-bin-dir', default=os.path.join(BASE_DIR, 'data-bin'))

    parser.add_argument('--add-word-ratio', action='store_true', default=False)