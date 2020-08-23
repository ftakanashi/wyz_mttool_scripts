#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
Given a list of files. Assert that all files have the same line number.
Analyze every line in the FIRST FILE and judge if the line is a with_match one or a non_match one.
(according to the -wmp and -nmp options)
Seperately write the line and every corresponding line which has the same index in each file into
respective divided files whose filenames contain with_match as flag.
'''

import argparse


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '--files', required=True, nargs='+',
                        help='Multiple files that needs to be divided.')

    parser.add_argument('-wmp', '--with-match-pattern', default=None,
                        help='DEFAULT: None')
    parser.add_argument('-nmp', '--non-match-pattern', default=None,
                        help='DEFAULT: None')

    opt = parser.parse_args()

    assert opt.with_match_pattern is not None or opt.non_match_pattern is not None,\
    'at least --with-match-pattern or --non-match-pattern should be specified.'

    return opt

def judge_line(line, opt):
    if opt.with_match_pattern is not None:
        return opt.with_match_pattern in line

    else:
        return opt.non_match_pattern not in line

def main():
    opt = parse_args()

    content = []
    for fn in opt.files:
        print(f'Reading {fn} lines...')
        with open(fn, 'r') as f:
            content.append([l.strip() for l in f])

    pivot_lines = content[0]
    for i, lines in enumerate(content):
        assert len(pivot_lines) == len(lines), f'{opt.files[i]} seems do not have valid line number.' \
                                               f'{opt.files[0]} has {len(content[0])} lines and ' \
                                               f'{opt.files[i]} has {len(content[i])} lines.'

    print('Creating writing files...')
    wfs = []
    def getfn(fn, flag):
        s = fn.split('.')
        return f'{".".join(s[:-1])}.{flag}.{s[-1]}'
    for i in range(len(content)):
        wm_wf = open(getfn(opt.files[i], 'with_match'), 'w')
        nm_wf = open(getfn(opt.files[i], 'non_match'), 'w')
        wfs.append((wm_wf, nm_wf))

    print('Writing results...')
    with_match_count = non_match_count = 0
    for line_i, line in enumerate(pivot_lines):
        with_match = judge_line(line, opt)
        if with_match:
            wf_i = 0
            with_match_count += 1
        else:
            wf_i = 1
            non_match_count += 1
        for i in range(len(content)):
            wfs[i][wf_i].write(content[i][line_i] + '\n')
    print(f'{with_match_count} lines are with_match.\n{non_match_count} lines are non_match.')

    for wm_wf, nm_wf in wfs:
        wm_wf.close()
        nm_wf.close()

if __name__ == '__main__':
    main()