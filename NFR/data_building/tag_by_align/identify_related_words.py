#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse


def parse_args():
    parser = argparse.ArgumentParser(usage='Identify related words in tmt based on the '
                                           '1. LCS between source and tms'
                                           '2. word alignment between tms and tmt')

    parser.add_argument('-s', '--src', required=True,
                        help='Path to the plain source file.')
    parser.add_argument('-tms', required=True)
    parser.add_argument('-tmt', required=True)
    parser.add_argument('--match-file', required=True,
                        help='Match file indicating the relationship between source and TMS.')
    parser.add_argument('-a', '--alignment', required=True,
                        help='Alignment file indicating the relationship between TMS and TMT.')
    parser.add_argument('-o', '--output', required=True)

    parser.add_argument('--source-tag', default='0',
                        help='DEFAULT: 0')
    parser.add_argument('--relate-tag', default='1',
                        help='DEFAULT: 1')
    parser.add_argument('--unrelate-tag', default='2',
                        help='DEFAULT: 2')
    parser.add_argument('--concat-tag', default=None,
                        help='DEFAULT: None. If set to None, will use the unrelate_tag.')

    args = parser.parse_args()

    return args


def find_longest_common_subsequences(seq_1, seq_2, sep=' '):
    # Ensure the smaller of the two sequences is used to create the columns for
    # the DP table.
    flag = 'col'
    if len(seq_1) < len(seq_2):
        new_seq_1 = seq_2
        seq_2 = seq_1
        seq_1 = new_seq_1
        flag = 'row'

    seq_1_len = len(seq_1)
    seq_2_len = len(seq_2)
    seq_1_len_plus_1 = seq_1_len + 1
    seq_2_len_plus_1 = seq_2_len + 1

    subseq_last_row = [''] * seq_2_len_plus_1
    subseq_current_row = [''] + [''] * seq_2_len

    for row in range(1, seq_1_len_plus_1):

        for col in range(1, seq_2_len_plus_1):

            if seq_1[row - 1] == seq_2[col - 1]:
                diagonal_cell_value = subseq_last_row[col - 1]
                # matched_element = seq_1[row-1]
                if flag == 'col':  # seq_2 corresponds to tms
                    rec = col - 1
                else:  # seq_1 corresponds to tms
                    rec = row - 1
                new_cell_value = f'{diagonal_cell_value}{sep}{rec}'
            else:
                above_set = subseq_last_row[col]
                left_set = subseq_current_row[col - 1]
                if len(above_set) >= len(left_set):
                    new_cell_value = above_set
                else:
                    new_cell_value = left_set
            subseq_current_row[col] = new_cell_value

        subseq_last_row = subseq_current_row
        subseq_current_row = [''] + [''] * seq_2_len

    return [int(i) for i in subseq_last_row[-1].split()]


def process_one_line(src_tokens, tms_tokens, tmt_tokens, aligns, opt):
    # find the LCS of src_line and tms_line
    # record the indices of LCS's tokens in tms_line
    lcs_indices = find_longest_common_subsequences(src_tokens, tms_tokens)

    # re-arrange the alignment information into a list of tuple and from the "target" perspective
    align_info = []
    for p in aligns:
        s_i, t_i = p.split('-')
        s_i, t_i = int(s_i), int(t_i)
        align_info.append((t_i, s_i))

    # iterate every possible pair of t-s alignment and filter out the indices of the related words
    # referring to paper: Boosting Neural Machine Translation with Similar Translations(ACL2020)
    set_pos = set([])
    set_neg = set([])

    for t in range(len(tmt_tokens)):
        neg_flag = True
        for s in range(len(tms_tokens)):
            if (t, s) in align_info and s in lcs_indices:
                set_pos.add(t)
            elif (t, s) in align_info and s not in lcs_indices:
                neg_flag = False
        if neg_flag:
            set_neg.add(t)

    final_set = set_pos.intersection(set_neg)

    # 1: T  2: R
    map_table = [opt.relate_tag if t in final_set else opt.unrelate_tag for t in range(len(tmt_tokens))]
    concat_tag = opt.concat_tag if opt.concat_tag is not None else opt.unrelate_tag
    map_table = [opt.source_tag] * len(src_tokens) + [concat_tag] + map_table

    return map_table


def main():
    opt = parse_args()

    print('Reading source lines...')
    with open(opt.src, 'r') as f:
        src_lines = [l.strip() for l in f]

    print('Reading TMS lines...')
    with open(opt.tms, 'r') as f:
        tms_lines = [l.strip() for l in f]

    print('Reading TMT lines...')
    with open(opt.tmt, 'r') as f:
        tmt_lines = [l.strip() for l in f]

    print('Reading match file lines...')
    with open(opt.match_file, 'r') as f:
        match_lines = [l.strip() for l in f]

    print('Reading alignment lines...')
    with open(opt.alignment, 'r') as f:
        align_lines = [l.strip() for l in f]

    assert len(src_lines) == len(match_lines), 'Every source line should and have to have one row of match ' \
                                               'information(if no match, then leave an empty row)'

    assert len(tms_lines) == len(tmt_lines)
    assert len(tms_lines) == len(align_lines), 'TMS and TMT alignment information should be integrated.'

    wf = open(opt.output, 'w')
    for i, src_line in enumerate(src_lines):
        match_line = match_lines[i]
        src_tokens = src_line.strip().split()
        # only one-best is supported now.
        if match_line.strip() != '':
            tm_i = int(match_line.strip().split('|||')[0].split()[0])
            tms_line = tms_lines[tm_i]
            tmt_line = tmt_lines[tm_i]
            align_line = align_lines[tm_i]

            tms_tokens = tms_line.strip().split()
            tmt_tokens = tmt_line.strip().split()
            aligns = align_line.strip().split()
            line_res = process_one_line(src_tokens, tms_tokens, tmt_tokens, aligns, opt)
        else:
            line_res = [opt.source_tag] * len(src_tokens)

        wf.write(' '.join([f'{i}' for i in line_res]) + '\n')


if __name__ == '__main__':
    main()
