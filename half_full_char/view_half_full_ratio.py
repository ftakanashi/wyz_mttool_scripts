#!/usr/bin/env python
# -*- coding:utf-8 -*-

import collections
import string
import sys

HALF_CHAR = range(0x0020, 0x7e+1)
FULL_CHAR = [0x3000,] + [c+0xfee0 for c in HALF_CHAR[1:]]

def tongji_ch(ch, count_dict):
    ch = chr(ch)
    if ch in string.digits:
        count_dict['digit'] += 1
    elif ch in string.ascii_letters:
        count_dict['letters'] += 1
    elif ch in string.punctuation:
        count_dict['punc'] += 1
    else:
        count_dict['other'] += 1

def main():
    content = sys.stdin.read()
    total_count = 0
    half_count = collections.defaultdict(int)
    full_count = collections.defaultdict(int)
    for ch in content:
        total_count += 1
        ch = ord(ch)
        if ch in HALF_CHAR:
            tongji_ch(ch, half_count)
        elif ch in FULL_CHAR:
            dummy_half = ch - 0xfee0 if ch != 0x3000 else 0x0020
            tongji_ch(dummy_half, full_count)

    print('{} chars are counted.'.format(total_count))
    print('Among all HALF chars:\n{}'.format('\n'.join(['{}: {}'.format(k,v) for k,v in half_count.items()])))
    print('Among all FULL chars:\n{}'.format('\n'.join(['{}: {}'.format(k,v) for k,v in full_count.items()])))

if __name__ == '__main__':
    main()
