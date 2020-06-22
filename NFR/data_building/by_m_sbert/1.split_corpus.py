#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import os

def process(opt):
    with open(opt.input, 'r') as f:
        lines = f.readlines()

    input_fn = os.path.basename(opt.input)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, opt.output_dir)
    os.makedirs(output_path, exist_ok=True)

    f_i, s_i = 0, 0
    stride = opt.max_shard_length
    while s_i < len(lines):
        print(os.path.join(output_path, f'{input_fn}.{f_i}'))
        with open(os.path.join(output_path, f'{input_fn}.{f_i}'), 'w') as f:
            f.writelines(lines[s_i:s_i+stride])
        s_i += stride
        f_i += 1


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input', required=True,
                        help='Path to the input file.')
    parser.add_argument('-o', '--output-dir', default='splited')
    parser.add_argument('-n', '--max-shard-length', type=int, required=True)

    opt = parser.parse_args()

    process(opt)

if __name__ == '__main__':
    main()