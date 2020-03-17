#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import collections
import os

def split_by_len(opt):
    with open(opt.source, 'r') as f:
        src_lines = f.readlines()

    with open(opt.reference, 'r') as f:
        ref_lines = f.readlines()

    with open(opt.hypothesis, 'r') as f:
        hyp_lines = f.readlines()

    assert len(src_lines) == len(ref_lines)
    assert len(src_lines) == len(hyp_lines)

    res = collections.defaultdict(list)
    max_len_limit = int(opt.max_len_limit)
    for i, src_line in enumerate(src_lines):
        ref_line = ref_lines[i]
        hyp_line = hyp_lines[i]
        len_cate = len(src_line.strip().split())
        res[len_cate].append((ref_line, hyp_line))

    for len_cate, content in res.items():
        if len_cate <= max_len_limit:
            len_ref_fn = os.path.join('splited', '{}.{}'.format(opt.reference, len_cate))
            len_hyp_fn = os.path.join('splited', '{}.{}'.format(opt.hypothesis, len_cate))
            len_ref_file = open(len_ref_fn, 'w')
            len_hyp_file = open(len_hyp_fn, 'w')
        else:
            len_ref_fn = os.path.join('splited', '{}.{}'.format(opt.reference, max_len_limit))
            len_hyp_fn = os.path.join('splited', '{}.{}'.format(opt.hypothesis, max_len_limit))
            len_ref_file = open(len_ref_fn, 'a')
            len_hyp_file = open(len_hyp_fn, 'a')

        for r,h in content:
            len_ref_file.write(r.strip() + '\n')
            len_hyp_file.write(h.strip() + '\n')

        len_ref_file.close(), len_hyp_file.close()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--source', required=True,
                        help='Path to the source file.')

    parser.add_argument('-r', '--reference', default=None,
                        help='Path to the reference file. Default is None means no reference file to split.')

    parser.add_argument('-p', '--hypothesis', required=True,
                        help='Path to the hypothesis file.')

    parser.add_argument('-M', '--max-len-limit', default=20, type=int,
                        help='A limit of max length. All rows above which will be counted in one set.')

    opt = parser.parse_args()

    os.system('mkdir splited')
    split_by_len(opt)

if __name__ == '__main__':
    main()