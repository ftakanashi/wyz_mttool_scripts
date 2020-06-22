#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse

def process(opt):
    with open(opt.with_match_ref, 'r') as f:
        with_match_ref_lines = f.readlines()

    with open(opt.non_match_ref, 'r') as f:
        non_match_ref_lines = f.readlines()

    with open(opt.original_ref, 'r') as f:
        original_ref_lines = f.readlines()

    with open(opt.with_match_hyp, 'r') as f:
        with_match_hyp_lines = f.readlines()

    with open(opt.non_match_hyp, 'r') as f:
        non_match_hyp_lines = f.readlines()

    slots = [None] * len(original_ref_lines)
    for i, with_match_ref_line in enumerate(with_match_ref_lines):
        orig_i = original_ref_lines.index(with_match_ref_line)
        assert orig_i != -1
        original_ref_lines[orig_i] = None
        slots[orig_i] = with_match_hyp_lines[i]
    for i, non_match_ref_line in enumerate(non_match_ref_lines):
        orig_i = original_ref_lines.index(non_match_ref_line)
        assert orig_i != -1
        original_ref_lines[orig_i] = None
        slots[orig_i] = non_match_hyp_lines[i]

    with open(opt.output, 'w') as f:
        f.writelines(slots)

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--with-match-ref', required=True)
    parser.add_argument('--non-match-ref', required=True)
    parser.add_argument('--original-ref', required=True)
    parser.add_argument('--with-match-hyp', required=True)
    parser.add_argument('--non-match-hyp', required=True)

    parser.add_argument('--output', required=True)

    opt = parser.parse_args()

    process(opt)

if __name__ == '__main__':
    main()