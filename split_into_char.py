#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True,
                        help='Path to the input file.')
    parser.add_argument('-o', '--output', required=True,
                        help='Path to the output file.')


    opt = parser.parse_args()

    with open(opt.input, 'r') as f:
        input_lines = f.readlines()

    fw = open(opt.output, 'w')
    for l in input_lines:
        new_line = []
        for ch in list(l.strip()):
            if ch != ' ': new_line.append(ch)

        new_line = ' '.join(new_line)
        fw.write('{}\n'.format(new_line))

if __name__ == '__main__':
    main()