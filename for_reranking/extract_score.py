#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import re

def main():
    lines = sys.stdin.read().split('\n')
    container = {}
    for line in lines:
        m = re.search('^H\-(\d+?)\t(.+?)\t', line)
        if m is not None:
            sid = int(m.group(1))
            score = float(m.group(2))
            container[sid] = score

    for sid in sorted(container):
        print(container[sid])

if __name__ == '__main__':
    main()
