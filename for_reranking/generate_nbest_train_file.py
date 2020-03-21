#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-n', required=True,
                        help='Number of translation candidates.')
    parser.add_argument('--hyp', required=True,
                        help='Path to the hypothesis file.')
    parser.add_argument('--total-score', required=True,
                        help='Path to the total.score')
    parser.add_argument('--origin-score', required=True,
                        help='Path to the original score file.')
    parser.add_argument('--output', required=True,
                        help='Path to the output file.')

    opt = parser.parse_args()

    parallel_n = int(opt.n)

    with open(opt.hyp, 'r') as f:
        hyp_lines = f.readlines()

    with open(opt.total_score, 'r') as f:
        total_score_lines = f.readlines()

    with open(opt.origin_score, 'r') as f:
        origin_score_lines = f.readlines()

    fw = open(opt.output, 'w')
    for i, hyp in enumerate(hyp_lines):
        total_score = total_score_lines[i]
        origin_score = origin_score_lines[i]
        fw.write('{} ||| {} ||| {} ||| {}\n'.format(
            i // parallel_n, hyp.strip(), total_score.strip(), origin_score.strip()
        ))

    fw.close()

if __name__ == '__main__':
    main()