#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys

def main():
    nfr_fn = sys.argv[1]
    bkf_res_fn = sys.argv[2]
    bkf_aug_fn = sys.argv[3]

    with open(nfr_fn, 'r') as f:
        nfr_lines = f.readlines()

    with open(bkf_res_fn, 'r') as f:
        bkf_res_lines = f.readlines()

    fw = open(bkf_aug_fn, 'w')

    for i,l in enumerate(nfr_lines):
        if '@@@ [BLANK] @@@ [BLANK] @@@ [BLANK]' in l:
            l = l.strip().replace('@@@ [BLANK] @@@ [BLANK] @@@ [BLANK]', '')
            fw.write(f'{l} @@@ {bkf_res_lines[i].strip()} @@@ [BLANK] @@@ [BLANK]\n')
        else:
            fw.write(l)

    fw.close()

if __name__ == '__main__':
    main()