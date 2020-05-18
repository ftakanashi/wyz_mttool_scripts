#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--src', required=True,
                        help='Source Language')
    parser.add_argument('-t', '--tgt', required=True,
                        help='Target Language.')
    parser.add_argument('-p', '--prefix', required=True,
                        help='Prefix of parallel corpus files.')
    parser.add_argument('--symbol-str', default='@@@ [BLANK] @@@ [BLANK] @@@ [BLANK]',
                        help='Symbol string of a non-match line.')

    opt = parser.parse_args()

    with open(f'{opt.prefix}.{opt.src}', 'r') as f:
        src_lines = f.readlines()

    with open(f'{opt.prefix}.{opt.tgt}', 'r') as f:
        tgt_lines = f.readlines()

    fw_1 = open(f'{opt.prefix}.with_match.{opt.src}', 'w')
    fw_2 = open(f'{opt.prefix}.with_match.{opt.tgt}', 'w')
    fw_3 = open(f'{opt.prefix}.non_match.{opt.src}', 'w')
    fw_4 = open(f'{opt.prefix}.non_match.{opt.tgt}', 'w')
    for i, l in enumerate(src_lines):
        if opt.symbol_str in l:
            fw_3.write(l.strip() + '\n')
            fw_4.write(tgt_lines[i].strip() + '\n')
        else:
            fw_1.write(l.strip() + '\n')
            fw_2.write(tgt_lines[i].strip() + '\n')

    for fw in (fw_1,fw_2,fw_3,fw_4):
        fw.close()

    print('ATTENTION: Do you need to manually remove the blank symbols?')

if __name__ == '__main__':
    main()
