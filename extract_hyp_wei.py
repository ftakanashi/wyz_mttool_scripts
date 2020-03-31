#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
Extract all hypothesis rows in a generate log file produced by fairseq/generate.py
NOTE: fairseq <= 0.8.0 may place a sum of log probabilities before the first token of the row. Remember to remove it
if you need to calculate BLEU score later.
'''

import argparse
import codecs
import re

from tqdm import tqdm

# PATTERN_TEMP = '{}\-(\d+).*\t(.+?)$'
PATTERN_TEMP = '{}\-(\d+).*\t(.*?)$'

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-t', '--target', default='hyp',
                        help='Specify the type of row. Options: hyp, src, tgt')

    parser.add_argument('-i', '--input', required=True,
                        help='Path to the input file.')
    parser.add_argument('-o', '--output', required=True,
                        help='Path to the output file.')

    parser.add_argument('--remain-id', action='store_true',
                        help='Specify to remain row ids and output rows in order of ids.')
    parser.add_argument('--remain-log-order', action='store_true',
                        help='Remaining the order in log file rather than order by id.')
    parser.add_argument('--no-progressbar', action='store_true',
                        help='Hide Progress Bar')
    parser.add_argument('--clear-space', action='store_true',
                        help='Specify to clear all space between tokens in output.')

    opt = parser.parse_args()

    if opt.target not in ('hyp', 'src', 'tgt'):
        raise Exception('Invalid target option [{}]'.format(opt.target))

    if opt.target == 'hyp':
        PATTERN = PATTERN_TEMP.format('H')
    elif opt.target == 'src':
        PATTERN = PATTERN_TEMP.format('S')
    else:
        PATTERN = PATTERN_TEMP.format('T')

    fr = codecs.open(opt.input, 'r', encoding='utf-8')

    output_content = []
    for line in tqdm(fr, mininterval=0.5, ncols=50, desc='Reading Data'):
        m = re.search(PATTERN, line)
        if m is not None:
            output_content.append(
                    {'id': int(m.group(1)), 'content': m.group(2)}
            )

    fo = codecs.open(opt.output, 'w', encoding='utf-8')
    if opt.remain_log_order:
        ite = output_content
    else:
        ite = sorted(output_content, key=lambda x:x['id'])

    for item in tqdm(ite, mininterval=0.5, ncols=50, desc='Writing Data'):
        content = item['content']
        if opt.clear_space:
            if opt.remain_id:
                fo.write('{}\t'.format(item['id']))
            fo.write(''.join(content.strip().split(' ')) + '\n')
        else:
            if opt.remain_id:
                fo.write('{}\t'.format(item['id']))
            fo.write(content.strip() + '\n')

    fr.close()
    fo.close()

if __name__ == '__main__':
    main()



