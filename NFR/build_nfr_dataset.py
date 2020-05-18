#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
This script can accept a query file and build a augmented source corpus file by using SetSimilaritySearch and EditDistance.
'''

import argparse
import editdistance
from tqdm import tqdm
from SetSimilaritySearch import SearchIndex as SI


def distance_score(a, b):
    '''
    The original editdistance library only return an absolute distance figure.
    By dividing by the longer length among a and b, change it into a score by which the similarity can be mesured in
    a soft way(0-totally different, 1-identical)
    '''
    distance = editdistance.eval(a, b)
    longer_len = max(len(a), len(b))
    return 1 - float(distance) / longer_len


def match_fuzzy(query, search_index, opt):
    if type(query) is not list:
        query = query.strip().split()

    if opt.include_perfect_match:
        flag = 99999
    else:
        flag = 1.0
    cand_indices = [t[0] for t in list(sorted(search_index.query(query), key=lambda x: x[1], reverse=True)) if
                    t[1] < flag]

    return cand_indices[:opt.sss_nbest]


def calc_edit_distance(query, cand_indices, tms_lines):
    candidates = [tms_lines[i].strip().split() for i in cand_indices]
    res = {}
    if type(query) is not list:
        query = query.strip().split()
    for i, c in enumerate(candidates):
        res[cand_indices[i]] = distance_score(query, c)

    return sorted(res, key=lambda x: res[x], reverse=True)


def process(opt):
    print('Reading query data...')
    with open(opt.query, 'r') as f:
        query_lines = f.readlines()

    print('Reading source side translation memory data...')
    with open(opt.translation_memory_src, 'r') as f:
        tms_lines = f.readlines()

    print('Reading target side translation memory data...')
    with open(opt.translation_memory_tgt, 'r') as f:
        tmt_lines = f.readlines()

    print('Building Search Index...')
    search_index = SI([l.strip().split() for l in tms_lines],
                      similarity_threshold=opt.sss_lambda)

    wf = open(opt.output, 'w')
    CACHE = {}
    for q in tqdm(query_lines, mininterval=1.0, ncols=100, leave=True):
        if q not in CACHE:
            cand_indices = match_fuzzy(q, search_index, opt)

            cand_indices = calc_edit_distance(q, cand_indices, tms_lines)

            appendix = []
            for i in range(opt.format_n):
                try:
                    tmt_i = cand_indices[i]
                except IndexError as e:
                    appendix.append(opt.blank_symbol)
                else:
                    appendix.append(tmt_lines[tmt_i].strip())

            appendix_str = opt.concat_symbol.join(appendix)
            CACHE[q] = appendix_str
        else:
            appendix_str = CACHE[q]

        aug_query = f'{q.strip()}{opt.concat_symbol}{appendix_str}\n'
        wf.write(aug_query)

    wf.close()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-q', '--query', required=True,
                        help='Path to the query file.')
    parser.add_argument('-tms', '--translation-memory-src', required=True,
                        help='Path to the source side translation memory file.')
    parser.add_argument('-tmt', '--translation-memory-tgt', required=True,
                        help='Path to the target side translation memory file.')
    parser.add_argument('-o', '--output', required=True,
                        help='Path to the output file.')

    parser.add_argument('-sss-nbest', default=2000, type=int,
                        help='N Best similar sentences selected by SetSimilaritySearch.')
    parser.add_argument('-sss-lambda', default=0.5, type=float,
                        help='Threshold for SetSimilaritySearch')
    parser.add_argument('--include-perfect-match', action='store_true', default=False,
                        help='Perfect match will be included during sss.')
    parser.add_argument('--ed-lambda', default=0.5, type=float,
                        help='Threshold for edit distance score.')
    parser.add_argument('--format-n', default=3, type=int,
                        help='Deciding format N.')

    # parser.add_argument('-threads', default=1, type=int,    # todo multi-thread
    #                     help='Multi-threading.')

    parser.add_argument('--concat-symbol', default=' @@@ ')
    parser.add_argument('--blank-symbol', default='[BLANK]')

    opt = parser.parse_args()

    process(opt)

if __name__ == '__main__':
    main()