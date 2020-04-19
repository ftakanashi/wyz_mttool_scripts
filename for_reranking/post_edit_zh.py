#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import sys
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--comma', action='store_true')
    parser.add_argument('--bracket', action='store_true')
    parser.add_argument('--colon', action='store_true')
    parser.add_argument('--question-mark', action='store_true')
    parser.add_argument('--quotation-mark', action='store_true')
    parser.add_argument('--region-comma', action='store_true')

    opt = parser.parse_args()

    content = sys.stdin.read()

    if opt.comma:
        content = content.replace(',', '，')
    if opt.bracket:
        content = content.replace('(', '（').replace(')', '）')
    if opt.colon:
        content = content.replace(':', '：')
    if opt.question_mark:
        content = content.replace('?', '？')
    if opt.quotation_mark:
        content = content.replace('「', '“').replace('」', '”')

    if opt.region_comma:
        for ptn in '省市区县郡':
            re.sub(f'{ptn}( *?)[,，]', f'{ptn}\g<1>、', content)
            # content = content.replace(f'{ptn},', f'{ptn}、')

    print(content.strip())

if __name__ == '__main__':
    main()