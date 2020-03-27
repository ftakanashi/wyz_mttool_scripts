#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys

def main():
    lines = sys.stdin.read().split('\n')

    for line in lines:
        print(''.join(line.strip().split()))

if __name__ == '__main__':
    main()