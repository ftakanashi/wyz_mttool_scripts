#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse

def process(opt):
    with open(opt.input, 'r') as f:
        lines = [l.strip() for l in f]

    wf = open(opt.output, 'w')
    for l in lines:
        new_l = opt.delimeter.join(l.split(opt.delimeter)[:-1])
        wf.write(f'{new_l.strip()} {opt.delimeter}\n')

    wf.close()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input', required=True)
    parser.add_argument('-o', '--output', required=True)

    parser.add_argument('--delimeter', default='@@@',
                        help='DEFAULT: @@@')

    opt = parser.parse_args()

    process(opt)

if __name__ == '__main__':
    main()