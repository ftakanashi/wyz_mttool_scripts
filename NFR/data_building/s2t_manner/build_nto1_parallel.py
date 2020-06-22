#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
from tqdm import tqdm

def get_fn(fn, suf):
    e = fn.split('.')
    return '.'.join(e[:-1]) + f'.{suf}.{e[-1]}'

def process(opt):
    print('Reading Source File...')
    with open(opt.src, 'r') as f:
        src_lines = [l.strip() for l in f]

    print('Reading Target File...')
    with open(opt.tgt, 'r') as f:
        tgt_lines = [l.strip() for l in f]

    print('Reading TMS File...')
    with open(opt.tms, 'r') as f:
        tms_lines = [l.strip() for l in f]

    print('Reading TMT File...')
    with open(opt.tmt, 'r') as f:
        tmt_lines = [l.strip() for l in f]

    print('Reading Match File...')
    with open(opt.match_file, 'r') as f:
        match_lines = [l.strip() for l in f]

    assert len(src_lines) == len(match_lines)
    assert len(src_lines) == len(tgt_lines)
    assert len(tms_lines) == len(tmt_lines)

    print('Decoding Match File Information...')
    match_info = {}
    for line_no, match_line in enumerate(match_lines):
        match_line_info = []
        if match_line != '':
            for match_i_v in match_line.split(opt.match_file_delimeter):
                i, v = match_i_v.strip().split()
                match_line_info.append((int(i), float(v)))
        match_info[line_no] = match_line_info

    print('Processing source lines...')
    i = 0
    aug_src_lines = []
    aug_tgt_lines = []
    for src_line in tqdm(src_lines, mininterval=1, ncols=50):
        match_line_info = match_info[i]
        tgt_line = tgt_lines[i]
        match_src_lines = []
        for match_i, match_v in sorted(match_line_info, key=lambda x:x[1], reverse=True):
            if len(match_src_lines) >= opt.topk or match_v <= opt.threshold:
                break
            cand = tms_lines[match_i]
            if src_line == cand and not opt.include_perfect_match:
                continue
            if opt.permit_duplicate_match or cand not in match_src_lines:
                match_src_lines.append(cand)

        if len(match_src_lines) > 0:
            for match_src_line in match_src_lines:
                aug_src_lines.append(f'{match_src_line}{opt.concat_symbol}{src_line}')
                aug_tgt_lines.append(f'{tgt_line.strip()}\n')
        i += 1

    print('Writing augmented source lines...')
    wf = open(get_fn(opt.src, opt.output_flag), 'w')
    for aug_src_line in aug_src_lines:
        wf.write(f'{aug_src_line.strip()}\n')

    print('Writing augmented target lines...')
    wf = open(get_fn(opt.tgt, opt.output_flag), 'w')
    for aug_tgt_line in aug_tgt_lines:
        wf.write(f'{aug_tgt_line.strip()}\n')


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--src', required=True)
    parser.add_argument('-t', '--tgt', required=True)
    parser.add_argument('-tms', required=True)
    parser.add_argument('-tmt', required=True)
    parser.add_argument('--match-file', required=True)
    parser.add_argument('--output-flag', default='nto1',
                        help='DEFAULT: nto1')

    parser.add_argument('--match-file-delimeter', type=str, default='|||')
    parser.add_argument('--topk', type=int, default=3,
                        help='DEFAULT: 3')
    parser.add_argument('--concat-symbol', default=' @@@ ')
    parser.add_argument('--threshold', type=float, default=0.8,
                        help='DEFAULT: 0.8')

    parser.add_argument('--permit-duplicate-match', action='store_true', default=False)
    parser.add_argument('--include-perfect-match', action='store_true', default=False)

    opt = parser.parse_args()

    process(opt)

if __name__ == '__main__':
    main()