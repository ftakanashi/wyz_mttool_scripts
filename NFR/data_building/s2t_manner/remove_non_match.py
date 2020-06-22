#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse

def process(opt):
    print('Reading source file...')
    with open(f'{opt.prefix}.{opt.src_lang}', 'r') as f:
        src_lines = [l.strip() for l in f]

    print('Reading target file...')
    with open(f'{opt.prefix}.{opt.tgt_lang}', 'r') as f:
        tgt_lines = [l.strip() for l in f]


    assert len(src_lines) == len(tgt_lines)
    non_match_res = []
    with_match_res = []

    for i, src_line in enumerate(src_lines):
        tgt_line = tgt_lines[i]
        if '@@@' not in src_line and '@@@' not in tgt_line:
            non_match_res.append((src_line, tgt_line))
        else:
            with_match_res.append((src_line, tgt_line))

    non_s = open(f'{opt.prefix}.non_match.{opt.src_lang}', 'w')
    non_t = open(f'{opt.prefix}.non_match.{opt.tgt_lang}', 'w')
    with_s = open(f'{opt.prefix}.with_match.{opt.src_lang}', 'w')
    with_t = open(f'{opt.prefix}.with_match.{opt.tgt_lang}', 'w')
    for s, t in non_match_res:
        non_s.write(f'{s.strip()}\n')
        non_t.write(f'{t.strip()}\n')
    for s, t in with_match_res:
        with_s.write(f'{s.strip()}\n')
        with_t.write(f'{t.strip()}\n')

    for f in (non_s, non_t, with_s, with_t):
        f.close()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--prefix', required=True)
    parser.add_argument('-s', '--src-lang', required=True)
    parser.add_argument('-t', '--tgt-lang', required=True)

    opt = parser.parse_args()

    process(opt)

if __name__ == '__main__':
    main()