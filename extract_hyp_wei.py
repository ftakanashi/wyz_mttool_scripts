#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import codecs
import re

from tqdm import tqdm


PATTERN_TEMP = '{}\-(\d+).*\t(.+?)$'

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
    parser.add_argument('--order-by-id', action='store_true',
                        help='Order the output by id.')
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
    if opt.order_by_id:
        ite = sorted(output_content, key=lambda x:x['id'])
    else:
        ite = output_content

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



