#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys

def main():
    lines = sys.stdin.read().split('\n')
    print(max([len(l.strip().split()) for l in lines]))

if __name__ == '__main__':
    main()