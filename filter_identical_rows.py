#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse

class Row(object):
    def __init__(self, idx, raw):
        self.idx = idx
        self.raw = raw

    def __eq__(self, other):
        return self.raw == other.raw

    def __hash__(self):
        return hash(self.raw)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--source', required=True,
                        help='Path to the source corpus.')
    parser.add_argument('-t', '--target', required=True,
                        help='Path to the target corpus.')

    opt = parser.parse_args()

    with open(opt.source, 'r') as f:
        src_lines = f.readlines()

    with open(opt.target, 'r') as f:
        tgt_lines = f.readlines()

    src_rows = [Row(i, line) for i, line in enumerate(src_lines)]
    tgt_rows = [Row(i, line) for i, line in enumerate(tgt_lines)]

