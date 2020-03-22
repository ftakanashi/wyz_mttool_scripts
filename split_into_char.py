#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys

def main():
    lines = sys.stdin.read().split('\n')

    for line in lines:
        if line.strip() == '': continue
        valid_chars = []
        for ch in line.strip():
            if ch.strip() != '':
                valid_chars.append(ch)

        print(' '.join(valid_chars))

if __name__ == '__main__':
    main()