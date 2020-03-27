#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import string
import sys

VALID_MODE = ['h2f', 'f2h']
VALID_GROUP = ['digits', 'letters', 'punctuations', 'all']
HALF_CHAR = range(0x0020, 0x7e+1)
FULL_CHAR = [0x3000,] + [c+0xfee0 for c in HALF_CHAR[1:]]

def process_ch(ch, opt):

    if ch in opt.exception:
        return ch
    
    group = opt.toggle_group
    if opt.mode == 'h2f' and ord(ch) in HALF_CHAR:
        if group == 'all' or \
            (group == 'digits' and ch in string.digits) or \
            (group == 'letters' and ch in string.ascii_letters) or \
            (group == 'punctuations' and ch in string.punctuation):
            return chr(ord(ch) + 0xfee0) if ord(ch) != 0x0020 else chr(0x3000)
    elif opt.mode == 'f2h' and ord(ch) in FULL_CHAR:
        dummy_half = chr(ord(ch) - 0xfee0) if ord(ch) != 0x3000 else chr(0x0020)
        if group == 'all' or \
            (group == 'digits' and dummy_half in string.digits) or \
            (group == 'letters' and dummy_half in string.ascii_letters) or \
            (group == 'punctuations' and dummy_half in string.punctuation):
            return dummy_half
    return ch


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('--mode', requied=True,
                        help='Specify the mode of toggling. Valid options are h2f(half to full) and f2h(full to half)')
    parser.add_argument('--toggle-group', default='all',
                        help='Toggle only the specified type of characters. \
                        Options are [all, digits, letters, punctuations].\
                         Default option is all.')
    parser.add_argument('--exception', default='',
                        help='Specify some characters as exceptions that needs no toggling.')

    opt = parser.parse_args()

    if opt.mode not in VALID_MODE:
        raise Exception('Mode [{}] is invalid.'.format(opt.mode))
    if opt.toggle_group not in VALID_GROUP:
        raise Exception('Group [{}] is invalid.'.format(opt.toggle_group))

    content = sys.stdin.read()
    for ch in content:
        print(process_ch(ch, opt), end='')

if __name__ == '__main__':
    main()