#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys

def main():
    with open(sys.argv[1], 'r') as f:
        content = f.read().split()

    c = 0
    for t in content:
        if t == '@@@':
            c += 1

    print(c)

if __name__ == '__main__':
    main()