#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys

or_align_fn = sys.argv[1]
fa_align_fn = sys.argv[2]

with open(or_align_fn, 'r') as f:
    or_align_lines = [l.strip() for l in f]

with open(fa_align_fn, 'r') as f:
    fa_align_lines = [l.strip() for l in f]

sure_count = 0
possible_count = 0
overlap_pos_count = 0

def one2zero(aligns):
    n = []
    for a in aligns:
        if '-' in a:
            c = '-'
            i, j = a.split('-')
        elif 'p' in a:
            c = 'p'
            i, j = a.split('p')

        i, j = int(i), int(j)
        i -= 1
        j -= 1
        n.append(f'{i}{c}{j}')

    return n

new_align_lines = []
for i, or_align_line in enumerate(or_align_lines):
    or_aligns = or_align_line.split()
    or_aligns = one2zero(or_aligns)
    fa_aligns = fa_align_lines[i].split()
    new_aligns = []
    for or_align in or_aligns:
        if '-' in or_align:
            sure_count += 1
            new_aligns.append(or_align)
        else:
            possible_count += 1
            if or_align.replace('p', '-') in fa_aligns:
                overlap_pos_count += 1
                new_aligns.append(or_align.replace('p', '-'))
    new_align_line = ' '.join(new_aligns)
    new_align_lines.append(new_align_line)

print('\n'.join(new_align_lines))

# print(f'Sure: {sure_count}\nPossible: {possible_count}\nOverlapped Possible: {overlap_pos_count}')