#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
Clear the matched lines in both source and target file whose s/t ratio or t/s ratio is too big.
Still being testing...
'''

import argparse
import codecs

from tqdm import tqdm

def check_len(s_line, t_line, r, mlt):
    s_tokens = s_line.strip().split()
    t_tokens = t_line.strip().split()

    if len(s_tokens) <= mlt or len(t_tokens) <= mlt:
        return True

    st_ratio = float(len(s_tokens)) / float(len(t_tokens))
    ts_ratio = 1 / st_ratio
    if st_ratio > r or ts_ratio > r:
        print(st_ratio, ts_ratio)
        return False
    else:
        return True

def clean_len_not_match(opt):
    s_f = codecs.open(opt.source, 'r', encoding=opt.encoding)
    t_f = codecs.open(opt.target, 'r', encoding=opt.encoding)

    s_res = codecs.open('{}.clean'.format(opt.source), 'w', encoding=opt.encoding)
    t_res = codecs.open('{}.clean'.format(opt.target), 'w', encoding=opt.encoding)

    ratio = float(opt.ratio)
    mlt = int(opt.min_len_threshold)
    print('Reading Content...')
    s_lines = s_f.readlines()
    t_lines = t_f.readlines()

    assert len(s_lines) == len(t_lines)

    total_clean_cnt = 0
    i = 0
    for s_l in tqdm(s_lines, mininterval=0.5, ncols=50, desc='Scanning'):
        t_l = t_lines[i]
        flag = check_len(s_l, t_l, ratio, mlt)
        if flag:
            s_res.write(s_l)
            t_res.write(t_l)
        else:
            total_clean_cnt += 1

        i += 1

    s_f.close(), t_f.close()
    s_res.close(), t_res.close()

    print('Totally, [{}]LINES are cleaned.'.format(total_clean_cnt))


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--source', required=True,
                        help='Specify the path to the source corpus.')
    parser.add_argument('-t', '--target', required=True,
                        help='Specify the path to the target corpus.')
    # parser.add_argument('-o', '--output', required=True,
    #                     help='Specify the path to the output file.')
    parser.add_argument('-r', '--ratio', required=True,
                        help='Remove all the rows that s/t or t/s > ratio.\nUsually a figure that is over 1.0 such as 1.2')
    parser.add_argument('-e', '--encoding', default='utf-8',
                        help='Specify the codecs of files.')

    parser.add_argument('--min-len-threshold', default=3,
                        help='Row whose length is less than the specified value would be ignored.')

    opt = parser.parse_args()

    clean_len_not_match(opt)

if __name__ == '__main__':
    main()