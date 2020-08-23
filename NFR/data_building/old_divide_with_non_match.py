#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import re


def judge_one_pair(src_line, tgt_line, opt):

    if opt.with_match_pattern is not None:
        m = re.search(opt.with_match_pattern, src_line)
        return m is not None
    else:
        m = re.search(opt.non_match_pattern, src_line)
        return m is None

def process(opt):
    src_fn = f'{opt.prefix}.{opt.source_lang}'
    tgt_fn = f'{opt.prefix}.{opt.target_lang}'

    print('Reading source lines...')
    with open(src_fn, 'r') as f:
        src_lines = [l.strip() for l in f]

    print('Reading target lines...')
    with open(tgt_fn, 'r') as f:
        tgt_lines = [l.strip() for l in f]

    if opt.tag is not None:
        print('Reading tag lines...')
        tag_fn = f'{opt.tag}.tag'
        with open(tag_fn, 'r') as f:
            tag_lines = [l.strip() for l in f]
    else:
        tag_lines = None

    with_match_pairs, non_match_pairs = [], []
    for i, src_line in enumerate(src_lines):
        tgt_line = tgt_lines[i]

        if tag_lines is not None:
            tag_line = tag_lines[i]
        else:
            tag_line = None

        zip_lines = (src_line, tgt_line, tag_line)
        with_match = judge_one_pair(src_line, tgt_line, opt)
        if with_match:
            with_match_pairs.append(zip_lines)
        else:
            non_match_pairs.append(zip_lines)

    print(f'Among {len(src_lines)} pairs, {len(with_match_pairs)} pairs with match and {len(non_match_pairs)}'
          f' pairs without match.')

    with open(f'{opt.prefix}.with_match.{opt.source_lang}', 'w') as wm_src:
        with open(f'{opt.prefix}.with_match.{opt.target_lang}', 'w') as wm_tgt:
            with open(f'{opt.prefix}.non_match.{opt.source_lang}', 'w') as nm_src:
                with open(f'{opt.prefix}.non_match.{opt.target_lang}', 'w') as nm_tgt:

                    for wm_src_line, wm_tgt_line in with_match_pairs:
                        wm_src.write(wm_src_line + '\n')
                        wm_tgt.write(wm_tgt_line + '\n')
                    for nm_src_line, nm_tgt_line in non_match_pairs:
                        nm_src.write(nm_src_line + '\n')
                        nm_tgt.write(nm_tgt_line + '\n')

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--prefix',
                        help='Prefix of parallel corpus.')
    parser.add_argument('-s', '--source-lang',
                        help='Code for source language.')
    parser.add_argument('-t', '--target-lang',
                        help='Code for target language.')
    parser.add_argument('-tag', default=None,
                        help='NFR tag file for source corpus.')

    parser.add_argument('--with-match-pattern', default=None,
                        help='A regular expression pattern match every with_match line.')
    parser.add_argument('--non-match-pattern', default='@@@ \[BLANK\]',
                        help='A regular expression pattern match every non_match line.')

    opt = parser.parse_args()

    process(opt)

if __name__ == '__main__':
    main()