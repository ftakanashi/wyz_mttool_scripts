#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
Nagata san's paper: https://arxiv.org/pdf/2004.14516.pdf
Input:
  - source corpus
  - target corpus
  - golden alignment label
Work:
  build a SQuAD like and JSON-format data file in which each source **token**
  (currently source span is not considered) annotated in alignment file
  will be marked and the answer set to be the corresponding target tokens according to the alignment.
'''

import argparse
import collections
import copy
import json

def analyze_alignment(align_lines):
    res = []
    for align_line in align_lines:
        align_info = collections.defaultdict(list)
        aligns = align_line.strip().split()
        for align in aligns:
            s, t = align.split('-')
            s, t = int(s), int(t)
            align_info[s-1].append(t-1)
        res.append(align_info)

    return res

def calc_answer_start(tgt_tokens, target_span):
    start_tok_i = min(target_span)
    total_len = start_tok_i    # length of spaces
    for t in tgt_tokens[:start_tok_i]:
        total_len += len(t)
    return total_len

def make_aug_src(src_tokens, query_i):
    tmp = copy.copy(src_tokens)
    tmp.insert(query_i, '¶')
    tmp.insert(query_i+2, '¶')
    return ' '.join(tmp)

def process_one_pair(src_line, tgt_line, align, pair_id):
    src_tokens = src_line.split()
    tgt_tokens = tgt_line.split()
    context = tgt_line
    qas = []
    for i in range(len(src_tokens)):
        aug_src = make_aug_src(src_tokens, i)
        target_span = align[i]
        if len(target_span) == 0:
            is_impossible = True
            answer_start = -1
            text = ''
        else:
            is_impossible = False
            answer_start = calc_answer_start(tgt_tokens, target_span)
            if max(target_span) - min(target_span) > len(target_span) + 2:
                print(list(sorted(target_span)), pair_id)
                text = ' '.join([tgt_tokens[t] for t in sorted(target_span)])
            else:
                text = ' '.join(tgt_tokens[min(target_span):max(target_span)+1])
        qas.append({
            'id': f'{pair_id}_{i}',
            'question': aug_src,
            'answers': [{
                'answer_start': answer_start,
                'text': text
            }],
            'is_impossible': is_impossible
        })
    return {
        'context': context,
        'qas': qas
    }


def process(opt):
    with open(opt.src, 'r') as f:
        src_lines = [l.strip() for l in f]

    with open(opt.tgt, 'r') as f:
        tgt_lines = [l.strip() for l in f]

    with open(opt.align, 'r') as f:
        align_lines = [l.strip() for l in f]

    aligns = analyze_alignment(align_lines)

    data = []
    for i, src_line in enumerate(src_lines):
        tgt_line = tgt_lines[i]
        align = aligns[i]
        one_pair_res_para = process_one_pair(src_line, tgt_line, align, i)
        one_pair_res = {'paragraphs': [one_pair_res_para, ]}
        data.append(one_pair_res)

    res = {
        'version': 'v2.0',
        'data': data
    }

    content = json.dumps(res, indent=4)
    with open(opt.output, 'w', encoding='utf-8') as f:
        f.write(content)

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--src', required=True)
    parser.add_argument('-t', '--tgt', required=True)
    parser.add_argument('-a', '--align', required=True)
    parser.add_argument('-o', '--output', required=True)

    opt = parser.parse_args()

    process(opt)

if __name__ == '__main__':
    main()