#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
Analyze a prediction.json produced by BERT
Transferring it into a alignment file format like 1-2 2-3 3-3...
Among one pair of sentences, an alignment a-b will be recorded only when
the average of p_{a-b} in s2t and p_{b-a} in t2s is greater than the threshold.
'''

import argparse
import collections
import json

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--pred-json', required=True,
                        help='Path to prediction.json')
    parser.add_argument('-o', '--output', required=True)
    parser.add_argument('--prob-threshold', type=float, default=0.4)

    return parser.parse_args()

def get_info(data):
    '''
    extract information from prediction's json.
    for each sentence pair, a defaultdict with a default empty list will be used as a container to save the information
    about the alignments yield from both directions.
    Specifically, key is 'a-b' while a represents for an token index in source and b for target.
    Value of 'a-b' is a list containing probabilities fecthed from 'a_b_s2t' and 'b_a_t2s' items from the original
    json data.
    Note that the list shall never longer than 2.
    :param data:
    :return:
    '''
    info = {}
    for k in data:
        v = data[k]
        sent_id, tok_id, flag = k.split('_')
        sent_id, tok_id = int(sent_id), int(tok_id)
        if sent_id not in info:
            info[sent_id] = collections.defaultdict(list)
        if v == '': continue
        for target_tok_i in range(v[3], v[4] + 1):
            key_name = f'{tok_id}-{target_tok_i}' if flag == 's2t' else f'{target_tok_i}-{tok_id}'
            info[sent_id][key_name].append(v[5])

    return info

def process_one_line(sent_align_info, opt):
    '''
    iterate all possible pairs and only record those pairs with an average over threshold
    :param sent_align_info:
    :param opt:
    :return:
    '''

    alignments = [(int(k.split('-')[0]), int(k.split('-')[1])) for k in sent_align_info.keys()]
    max_src_length = max([a[0] for a in alignments]) + 1
    max_tgt_length = max([a[1] for a in alignments]) + 1

    valid_aligns = []
    for i in range(max_src_length):
        for j in range(max_tgt_length):
            probs = sent_align_info[f'{i}-{j}']
            assert len(probs) <= 2
            if sum(probs) / 2 > opt.prob_threshold:
                valid_aligns.append(f'{i}-{j}')

    return valid_aligns


def main():
    opt = parse_args()

    with open(opt.pred_json, 'r') as f:
        data = json.loads(f.read())

    info = get_info(data)

    wf = open(opt.output, 'w')

    for sent_id in sorted(info):
        aligns = process_one_line(info[sent_id], opt)
        wf.write(' '.join(aligns) + '\n')

if __name__ == '__main__':
    main()

