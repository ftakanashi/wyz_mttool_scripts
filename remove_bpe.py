#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
This script can remove bpe symbol in a corpus file.
It is written for unity with other tool scripts.
Or you can just run command: "sed -r 's/(@@ )|(@@ ?$)//g' <input_file> > <output_file>",
'''

import re
import sys

def main():
    lines = sys.stdin.read().split('\n')[:-1]
    ptn = re.compile('(@@ )|(@@ ?$)')
    for line in lines:
        print(ptn.sub('', line.strip()))

if __name__ == '__main__':
    main()
