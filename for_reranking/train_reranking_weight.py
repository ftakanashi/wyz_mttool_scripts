#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run(cmd):
    print(cmd)
    os.system(cmd)

def


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--src', required=True,
                        help='Source Language')
    parser.add_argument('-t', '--tgt', required=True,
                        help='Target Language')
    parser.add_argument('-n', '--repeat-number', required=True, type=int,
                        help='Repeat Number')

    parser.add_argument('--score-log-dir', required=True,
                        help='Path to the score log dir where total.score and other scores are saved.')

    parser.add_argument('--moses-script-dir', default='/root/work/smt/mosesdecoder/scripts/nbest-rescore')
    parser.add_argument('--tool-script-dir', default=os.path.join(BASE_DIR, 'wyz_mttool_scripts'))