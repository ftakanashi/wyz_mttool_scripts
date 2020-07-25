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


def analyze_alignment(align_lines, opt):
    res = []
    for align_line in align_lines:
        align_info = collections.defaultdict(list)
        aligns = align_line.strip().split()
        for align in aligns:
            if 'p' in align:
                if opt.only_sure: continue
                s, t = align.split('p')
            else:
                s, t = align.split('-')
            s, t = int(s), int(t)
            align_info[s - 1].append(t - 1)
        res.append(align_info)

    return res


def calc_answer_start(tgt_tokens, target_span):
    '''
    calculate the start index of answer in character unit.
    '''
    start_tok_i = min(target_span)
    total_len = start_tok_i  # length of spaces
    for t in tgt_tokens[:start_tok_i]:
        total_len += len(t)
    return total_len


def split_span(span):
    '''
    cut off a span whenever the element is non-continuous.
    E.g. [1,2,4,5,6,8]  ->  [[1,2], [4,5,6], [8,]]
    '''
    sorted_span = list(sorted(span))
    res = []
    tmp = [sorted_span[0], ]
    for cursor in sorted_span[1:]:
        if cursor - tmp[-1] == 1:
            tmp.append(cursor)
        else:
            res.append(tmp)
            tmp = [cursor, ]

    res.append(tmp)
    return res


def make_aug_src(src_tokens, query_i):
    tmp = copy.copy(src_tokens)
    tmp.insert(query_i, '¶')
    tmp.insert(query_i + 2, '¶')
    return ' '.join(tmp)


def process_one_pair(src_line, tgt_line, s2t_align, t2s_align, pair_id, opt):
    src_tokens = src_line.split()
    tgt_tokens = tgt_line.split()
    s2t_context = tgt_line
    t2s_context = src_line

    s2t_qas = []
    t2s_qas = []

    def process_line(from_tokens, to_tokens, align, res_container, pair_id, id_flag):
        for i in range(len(from_tokens)):
            aug = make_aug_src(from_tokens, i)  # insert special tokens to pack a source token
            to_span = align[i]  # a list of target tokens ids which are aligned to the source token. May be an empty
            # one.
            if len(to_span) == 0:
                # if there is no answer
                is_impossible = True
                answers = [{'answer_start': -1, 'text': ''}]
                res_container.append({
                    'id': f'{pair_id}_{i}_{id_flag}' if id_flag is not None else f'{pair_id}_{i}',
                    'question': aug,
                    'answers': answers,
                    'is_impossible': is_impossible
                })
            else:
                is_impossible = False
                spans = split_span(to_span)  # cut the non-continuous span into pieces

                if len(spans) > 1 and opt.split_multiple_answers:
                    # multiple answer will be recorded in different qas
                    for span_id, span in enumerate(spans):
                        answers = [{
                            'answer_start': calc_answer_start(to_tokens, span),
                            'text': ' '.join([to_tokens[t] for t in span])
                        }]
                        res_container.append({
                            'id': f'{pair_id}_{i}_{span_id}_{id_flag}' if id_flag is not None else \
                            f'{pair_id}_{i}_{span_id}',
                            'question': aug,
                            'answers': answers,
                            'is_impossible': is_impossible
                        })
                else:
                    # multiple answer will be written into one qa as a list.
                    answers = [{'answer_start': calc_answer_start(to_tokens, span),
                                'text': ' '.join([to_tokens[t] for t in span])}
                               for span in spans]

                    res_container.append({
                        'id': f'{pair_id}_{i}_{id_flag}' if id_flag is not None else f'{pair_id}_{i}',
                        'question': aug,
                        'answers': answers,
                        'is_impossible': is_impossible
                    })

    s2t_id_flag = 's2t' if opt.do_t2s else None
    process_line(src_tokens, tgt_tokens, s2t_align, s2t_qas, pair_id, s2t_id_flag)
    if opt.do_t2s:
        process_line(tgt_tokens, src_tokens, t2s_align, t2s_qas, pair_id, 't2s')

    if opt.do_t2s:
        return {
                   'context': s2t_context,
                   'qas': s2t_qas
               }, {
                   'context': t2s_context,
                   'qas': t2s_qas
               }
    else:
        return {
            'context': s2t_context,
            'qas': s2t_qas
        }


def reverse_align_lines(align_lines):
    '''
    reverse every pair in a set of align_lines.
    e.g. ['1-2 2-3', '1-3 3-3']  -->  ['2-1 3-2', '3-1 3-3']
    '''
    res = []
    delimeters = ['p', '-']
    for align_line in align_lines:
        aligns = align_line.split()
        new_aligns = []
        for align in aligns:
            for d in delimeters:
                if d in align:
                    a, b = align.split(d)
                    new_aligns.append(f'{b}{d}{a}')
                    break

        res.append(' '.join(new_aligns))

    return res


def process(opt):
    with open(opt.src, 'r') as f:
        src_lines = [l.strip() for l in f]

    with open(opt.tgt, 'r') as f:
        tgt_lines = [l.strip() for l in f]

    if opt.align is not None:
        with open(opt.align, 'r') as f:
            s2t_align_lines = [l.strip() for l in f]

        t2s_align_lines = reverse_align_lines(s2t_align_lines)
    else:
        s2t_align_lines = ['' for _ in range(len(src_lines))]
        t2s_align_lines = ['' for _ in range(len(tgt_lines))]

    s2t_aligns = analyze_alignment(s2t_align_lines, opt)
    t2s_aligns = analyze_alignment(t2s_align_lines, opt)

    data = []
    for i, src_line in enumerate(src_lines):
        tgt_line = tgt_lines[i]
        s2t_align = s2t_aligns[i]
        t2s_align = t2s_aligns[i]
        if opt.do_t2s:
            s2t_one_pair_res_para, t2s_one_pair_res_para = \
                process_one_pair(src_line, tgt_line, s2t_align, t2s_align, i, opt)
            data.append({'paragraphs': [s2t_one_pair_res_para, ]})
            data.append({'paragraphs': [t2s_one_pair_res_para, ]})
        else:
            one_pair_res_para = process_one_pair(src_line, tgt_line, s2t_align, t2s_align, i, opt)
            data.append({'paragraphs': [one_pair_res_para, ]})

    shard_len = len(data) // opt.shards
    for shard_i in range(opt.shards):
        data_split = data[shard_i*shard_len:(shard_i+1)*shard_len] if shard_i != opt.shards - 1 else data[
            shard_i*shard_len:]
        res = {
            'version': 'v2.0',
            'data': data_split
        }

        content = json.dumps(res, indent=4)
        if opt.shards == 1:
            fn = opt.output
        else:
            fn = f'{opt.output}.{shard_i}'
        with open(fn, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f'shard[{shard_i}] written')


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--src', required=True)
    parser.add_argument('-t', '--tgt', required=True)
    parser.add_argument('-a', '--align', default=None,
                        help='If set to None, it means that the data might be test data without golden tags.')
    parser.add_argument('-o', '--output', required=True)

    parser.add_argument('--only-sure', action='store_true', default=False)
    parser.add_argument('--do-t2s', action='store_true', default=False)
    parser.add_argument('--split-multiple-answers', action='store_true', default=False,
                        help='When a token is aligned to multiple spans, it is regarded to have multiple answers. In '
                             'SQuAD format, a question could have multiple answers by adding several elements into '
                             'answers\' list. But train data only requires one particular answer so add this option '
                             'when you are generating json for train set.')

    parser.add_argument('--shards', type=int, default=1,
                        help='When processing huge dataset, split the json into several shards.')

    opt = parser.parse_args()

    process(opt)


if __name__ == '__main__':
    main()
