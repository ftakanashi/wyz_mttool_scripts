#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from xml.etree import ElementTree

def main():
    fn = sys.argv[1]

    doc = ElementTree.parse(fn)
    body = doc.find('body')

    tus = body.getiterator('tu')

    src_lines = []
    tgt_lines = []
    count = 0
    for tu in tus:
        src, tgt = tu.findall('tuv')
        src_line = src.find('seg').text
        tgt_line = tgt.find('seg').text
        src_lines.append(src_line), tgt_lines.append(tgt_line)
        count += 1
        if count % 1000000 == 0:
            print(count)

    with open('src', 'w') as f:
        for l in src_lines:
            f.write(f'{l}\n')
    with open('tgt', 'w') as f:
        for l in tgt_lines:
            f.write(f'{l}\n')

if __name__ == '__main__':
    main()