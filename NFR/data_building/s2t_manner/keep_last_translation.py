#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input', required=True)
    parser.add_argument('-o', '--output', required=True)

    parser.add_argument('--delimeter', default='@@@',
                        help='DEFAULT: @@@')

    opt = parser.parse_args()

    with open(opt.input, 'r') as f:
        lines = [l.strip() for l in f]

    wf = open(opt.output, 'w')
    for i, l in enumerate(lines):
        if opt.delimeter in l:
            new_line = l.split(opt.delimeter)[-1]
        else:
            new_line = l
        wf.write(new_line.strip())
        wf.write('\n')

if __name__ == '__main__':
    main()

