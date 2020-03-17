#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import sys

bleu_log = sys.argv[1]

def main():
    with open(bleu_log, 'r') as f:
        bleu_lines = f.readlines()

    for l in bleu_lines:
        m = re.search('BLEU \= (.+?),', l)
        if m is not None:
            print(m.group(1))

if __name__ == '__main__':
    main()