#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--bracket', action='store_true')
    parser.add_argument('--question-mark', action='store_true')
    parser.add_argument('--colon', action='store_true')
    parser.add_argument('--percent', action='store_true')
    parser.add_argument('--slash', action='store_true')

    opt = parser.parse_args()

    content = sys.stdin.read()

    if opt.bracket:
        content = content.replace('(', '（').replace(')', '）')
    if opt.question_mark:
        content = content.replace('?', '？')
    if opt.colon:
        content = content.replace(':', '：')
    if opt.percent:
        content = content.replace('%', '％')
    if opt.slash:
        content = content.replace('/', '／')

    print(content)

if __name__ == '__main__':
    main()