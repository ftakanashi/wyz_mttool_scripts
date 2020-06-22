#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse

def merge_match_lines(concat, *args):
    std_len = len(args[0])
    for lines in args:
        assert len(lines) == std_len

    new_lines = []
    for line_no in range(std_len):
        new_line = concat.join([lines[line_no] for lines in args])
        new_lines.append(new_line)

    return new_lines


def process(opt):
    with open(opt.src, 'r') as f:
        src_lines = [l.strip() for l in f]

    with open(opt.tmt, 'r') as f:
        tmt_lines = [l.strip() for l in f]

    match_lines_set = []
    for fn in opt.match_file:
        with open(fn, 'r') as f:
            match_lines_set.append([l.strip() for l in f])

    merged_match_lines = merge_match_lines(opt.match_line_concat_symbol, *match_lines_set)

    fw = open(opt.output, 'w')

    for i, src_line in enumerate(src_lines):
        match_info_line = merged_match_lines[i]
        match_info = [(int(p.split()[0]), float(p.split()[1])) for p in match_info_line.split(opt.match_line_concat_symbol)]
        match_info.sort(key=lambda x:x[1], reverse=True)

        aug_query = []
        for match_i, match_v in match_info:
            if match_v <= opt.threshold:
                break
            tmt_line = tmt_lines[match_i]
            if opt.permit_duplicate_match or tmt_line not in aug_query:
                aug_query.append(tmt_line)

                if len(aug_query) == opt.topk:
                    break

        while len(aug_query) < opt.topk:
            aug_query.append(opt.blank_symbol)

        aug_query.insert(0, src_line)
        aug_query = opt.concat_symbol.join(aug_query)

        fw.write(f'{aug_query}\n')

    fw.close()

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--src', required=True,
                        help='Original corpus.')
    parser.add_argument('-o', '--output', required=True)
    parser.add_argument('--match-file', nargs='+', required=True,
                        help='Specify the match files which take records of laser matching. Multiple inputs are supported.')
    parser.add_argument('-tmt', required=True,
                        help='Target side of Translation Memory.')

    parser.add_argument('--topk', default=3, type=int,
                        help='DEFAULT: 3')
    parser.add_argument('--threshold', default=0.75, type=float,
                        help='DEFAULT: 0.75')
    parser.add_argument('--permit-duplicate-match', action='store_true', default=False)

    parser.add_argument('--concat-symbol', default=' @@@ ')
    parser.add_argument('--blank-symbol', default='[BLANK]')
    parser.add_argument('--match-line-concat-symbol', default=' ||| ')


    opt = parser.parse_args()
    process(opt)

if __name__ == '__main__':
    main()
    