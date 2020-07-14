#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import collections
import re

FACTOR_I_MAP = {
    'match': 0,
    'score': 1
}

def analyze_sent(lines, opt):
    res = {}
    for l in lines:
        if l == '': continue
        if 'src' not in res:
            m = re.match('^SENT (\d+): (.+?)$', l)
            res['id'] = int(m.group(1))
            res['src'] = ' '.join(eval(m.group(2))).split(opt.delimeter)[-1].strip()
        elif 'pred' not in res:
            m = re.match('^PRED (\d+): (.+?)$', l)
            assert res['id'] == int(m.group(1))
            res['pred'] = m.group(2)
        elif 'score' not in res:
            m = re.match('^PRED SCORE: (.+?)$', l)
            res['score'] = float(m.group(1))
        else:
            raise Exception(f'Redundant Row {l}')

    return res

def process(opt):
    print('Reading input file...')
    with open(opt.input, 'r', encoding='utf-8') as f:
        input_lines = [l.strip() for l in f]

    print('Reading origin source file...')
    with open(opt.origin_source, 'r', encoding='utf-8') as f:
        src_lines = [l.strip() for l in f]

    res_container = []
    sent_lines = []
    for l in input_lines:
        if l == '': continue
        if l.startswith('PRED AVG SCORE'): break    # last row
        sent_lines.append(l)
        if len(sent_lines) == 3:    # every 3 rows in a raw file corresponds to one source sentence
            res_container.append(analyze_sent(sent_lines, opt))
            sent_lines = []


    print('Reorganizing results...')
    res = collections.OrderedDict()
    for sent_info in sorted(res_container, key=lambda x:x['id']):
        src = sent_info['src']
        if src not in res:
            res[src] = [(sent_info['id'], sent_info['score'], sent_info['pred'])]
        else:
            res[src].append((sent_info['id'], sent_info['score'], sent_info['pred']))

    fw = open(opt.output, 'w', encoding='utf-8')
    factor_i = FACTOR_I_MAP[opt.best]

    for src in src_lines:
        cand_list = res[src]
        cand_list.sort(key=lambda x:x[factor_i])
        cand = cand_list[0][-1]
        fw.write(cand + '\n')
    fw.close()


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input', required=True)
    parser.add_argument('-o', '--output', required=True)
    parser.add_argument('-s', '--origin-source', required=True)

    parser.add_argument('--best', choices=['match', 'score'], default='score',
                        help='DEFAULT: score')
    parser.add_argument('--delimeter', default='@@@',
                        help='DEFAULT: @@@')
    parser.add_argument('--topk', default=3, type=int,
                        help='DEFAULT: 3')

    opt = parser.parse_args()

    process(opt)

if __name__ == '__main__':
    main()