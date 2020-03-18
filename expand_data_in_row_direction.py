#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input', required=True,
                        help='Path to the input file.')
    parser.add_argument('-o', '--output', required=True,
                        help='Path to the output file.')
    parser.add_argument('-n', required=True,
                        help='How many times to expand data.')

    opt = parser.parse_args()

    fr = open(opt.input, 'r')
    fw = open(opt.output, 'w')
    line = fr.readline()
    while line:
        for _ in range(opt.n):
            fw.write('{}\n'.format(line.strip()))
        line = fr.readline()

if __name__ == '__main__':
    main()