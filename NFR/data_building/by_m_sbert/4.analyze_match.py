#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse

import collections

def process(opt):

    container = collections.defaultdict(list)
    for shard_i in range(opt.max_shard_i + 1):
        fn = f'{opt.match_prefix}.{shard_i}'
        print(f'Processing {fn}...')
        with open(fn, 'r') as f:
            shard_lines = f.readlines()

        for i,shard_line in enumerate(shard_lines):
            line_res = [(float(span.strip().split()[0]),int(span.strip().split()[1])) for span in shard_line.strip().split('|||')]
            container[i].extend(line_res)

    src_fn = f'{opt.prefix}.{opt.src}'
    tgt_fn = f'{opt.prefix}.{opt.tgt}'

    with open(src_fn, 'r') as f:
        src_lines = f.readlines()
    with open(tgt_fn, 'r') as f:
        tgt_lines = f.readlines()
    with open(opt.tmt, 'r') as f:
        tmt_lines = f.readlines()

    assert len(src_lines) == len(tgt_lines)
    assert len(container) == len(src_lines)

    src_wf = open(f'{opt.prefix}.{opt.output_flag}.{opt.src}', 'w')
    tgt_wf = open(f'{opt.prefix}.{opt.output_flag}.{opt.tgt}', 'w')
    for row_i in sorted(container):
        candidates_info = container[row_i]
        candidates_info.sort(key=lambda x:x[0], reverse=True)
        tmp = [src_lines[row_i].strip(), ]
        for cand_v, cand_i in candidates_info:
            cand_str = tmt_lines[cand_i].strip()
            if cand_v > opt.match_prob_threshold and cand_str not in tmp:
                tmp.append(cand_str)
                if len(tmp) == opt.topk + 1:
                    break
        while len(tmp) < opt.topk + 1:
            tmp.append(opt.blank_symbol)

        aug_src = opt.concat_symbol.join(tmp)
        src_wf.write(aug_src + '\n')
        tgt_wf.write(tgt_lines[row_i].strip() + '\n')

    src_wf.close(), tgt_wf.close()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--prefix', required=True)
    parser.add_argument('-s', '--src', required=True)
    parser.add_argument('-t', '--tgt', required=True)
    parser.add_argument('-tmt', required=True)

    parser.add_argument('--output-flag', default='sbert',
                        help='DEFAULT: sbert')
    parser.add_argument('--match-prefix', default='splited/match',
                        help='DEFAULT: splited/match')
    parser.add_argument('--max-shard-i', default=9, type=int,
                        help='DEFAULT: 9')
    parser.add_argument('--topk', default=3, type=int,
                        help='DEFAULT: 3')
    parser.add_argument('--match-prob-threshold', default=0.5, type=float,
                        help='DEFAULT: 0.5')
    parser.add_argument('--concat-symbol', default=' @@@ ',
                        help='DEFAULT: " @@@ "')
    parser.add_argument('--blank-symbol', default='[BLANK]',
                        help='DEFAULT: [BLANK]')

    opt = parser.parse_args()

    process(opt)

if __name__ == '__main__':
    main()