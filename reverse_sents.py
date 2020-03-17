#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
This script can reverse every sentence in a corpus file.
'''

import argparse
import codecs
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True,
                        help='Path the input file.')
    parser.add_argument('-o', '--output', required=True,
                        help='Path the output file.')
    parser.add_argument('--encoding', default='utf-8',
                        help='Specify the encoding format.')

    opt = parser.parse_args()

    if not os.path.isfile(opt.input):
        raise Exception('[{}] is not a valid file.'.format(opt.input))

    with codecs.open(opt.input, 'r', encoding=opt.encoding) as f:
        lines = f.readlines()

    fw = codecs.open(opt.output, 'w', encoding=opt.encoding)
    for l in lines:
        tokens = l.strip().split()
        tokens.reverse()
        fw.write('{}\n'.format(' '.join(tokens)))
    fw.close()


if __name__ == '__main__':
    main()