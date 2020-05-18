#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys

def main():
    content = sys.stdin.read()
    print(content.replace('[BLANK]', ' '))

if __name__ == '__main__':
    main()