#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import collections

def main():
    prefix = sys.argv[1]
    max_n = int(sys.argv[2])
    res = collections.defaultdict(list)
    for f_i in range(max_n+1):
        f = open(f'{prefix}.{f_i}', 'r')
        lines = [l.strip() for l in f]
        for line_no, l in enumerate(lines):
            for p in l.split('|||'):
                v, i = p.strip().split()
                v = float(v)
                i = int(i)
                res[line_no].append((i, v))

    for line_no in sorted(res):
        s = ' ||| '.join([f'{i} {v}' for i,v in sorted(res[line_no], key=lambda x:x[1], reverse=True)])
        print(s)

if __name__ == '__main__':
    main()




