#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
Output a hypotheses file based on the condition of the source file.
i.e. A row in source file has no fuzzy match, then the corresponding hypothesis should be taken from backoff-results.
Otherwise, it should be taken from nfr-results.

*NOTE* You should assure that source/backoff-results/nfr-results can match each other in a row-wise manner.
'''

import argparse


def process(opt):
    if opt.need_backoff_symbol_str is None:
        no_match_symbol_str = f'{opt.concat_symbol.strip()} {opt.blank_symbol}'
        no_match_str = ' '.join([no_match_symbol_str,] * opt.format_n)
    else:
        no_match_str = opt.need_backoff_symbol_str

    print('Reading augmented source file...')
    with open(opt.aug_src, 'r') as f:
        aug_src_lines = f.readlines()

    print('Reading backoff results file...')
    with open(opt.backoff_results, 'r') as f:
        backoff_res_lines = f.readlines()

    print('Reading NFR results file...')
    with open(opt.nfr_results, 'r') as f:
        nfr_res_lines = f.readlines()

    i = 0
    use_backoff_count = 0
    res = []
    for src_line in aug_src_lines:
        if no_match_str in src_line:    # use backoff results
            res.append(backoff_res_lines[i])
            use_backoff_count += 1
        else:    # use nfr results
            res.append(nfr_res_lines[i])
        i += 1

    print(f'{use_backoff_count} Rows will use backoff results.')
    print('Writing mixed result file...')
    fw = open(opt.output, 'w')
    for l in res:
        fw.write(f'{l.strip()}\n')
    fw.close()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--aug-src', required=True,
                        help='Path to the augmented source file')
    parser.add_argument('-b', '--backoff-results', required=True,
                        help='Path to the backoff result file.')
    parser.add_argument('-n', '--nfr-results', required=True,
                        help='Path to the NFR result file.')
    parser.add_argument('-o', '--output', required=True,
                        help='Path to the output file containing mixed results.')

    parser.add_argument('--need-backoff-symbol-str', default=None,
                        help='Force to use backoff results if this string is specified and detected in a source row.')
    parser.add_argument('--concat-symbol', default=' @@@ ')
    parser.add_argument('--blank-symbol', default='[BLANK]')
    parser.add_argument('--format-n', default=3, type=int)

    opt = parser.parse_args()

    process(opt)

if __name__ == '__main__':
    main()