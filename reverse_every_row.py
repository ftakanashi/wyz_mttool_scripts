#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys

def main():
    lines = sys.stdin.read().split('\n')
    for line in lines:
        if line.strip() == '': continue
        tokens = line.strip().split()
        tokens.reverse()
        print(' '.join(tokens))

if __name__ == '__main__':
    main()