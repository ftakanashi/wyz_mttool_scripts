#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import collections
import pickle
import time
import torch

from tqdm import tqdm
from SetSimilaritySearch import SearchIndex
from transformers import AutoTokenizer

from bert_score.bert_score.utils import bert_cos_score_idf, get_model

def topk_bert_score(cand, refs, k, model, tokenizer, **kwargs):
    batch_size = kwargs.get('batch_size', 128)
    idf_dict = kwargs.get('idf_dict', False)
    verbose = kwargs.get('verbose', False)

    cands = [cand] * len(refs)

    all_preds = bert_cos_score_idf(
        model, refs, cands, tokenizer, idf_dict, batch_size=batch_size,
        verbose=verbose
    ).cpu()

    refs_f1_scores = all_preds[:, 2]
    return refs_f1_scores.topk(k)

def match_fuzzy(src_line, search_index, opt):
    src_line_set = list(set(src_line.split()))

    if opt.include_perfect_match:
        flag = 9999
    else:
        flag = 0.9999

    cand_is = [t[0] for t in list(sorted(search_index.query(src_line_set), key=lambda x:x[1], reverse=True))
               if t[1] < flag]

    return cand_is[:opt.sss_nbest]

def calc_bert_score(src_line, tms_lines, sss_cand_is, model, tokenizer, opt, **kwargs):
    small_tms_lines = [tms_lines[i] for i in sss_cand_is]
    idf_dict = kwargs.get('idf_dict')

    topk_v, topk_i = topk_bert_score(src_line, small_tms_lines, min(opt.topk, len(sss_cand_is)), model, tokenizer,
                                     idf_dict=idf_dict, batch_size=opt.batch_size, verbose=opt.verbose)

    real_topk_i = [sss_cand_is[i] for i in topk_i]

    res = list(zip(topk_v, real_topk_i))
    res.sort(key=lambda x:x[0], reverse=True)

    return res[:opt.topk]

def process(opt):

    print('Reading in source lines...')
    with open(opt.src, 'r', encoding='utf-8') as f:
        src_lines = [l.strip() for l in f]

    print('Reading in tms lines...')
    with open(opt.tms, 'r', encoding='utf-8') as f:
        tms_lines = [l.strip() for l in f]

    print('Reading in idf_dict cache...')
    with open(opt.idf_dict, 'rb') as f:
        non_default_idf_dict = pickle.load(f)
    idf_dict = collections.defaultdict(lambda x:non_default_idf_dict.pop('default_value'))
    idf_dict.update(non_default_idf_dict)

    print('Building search index...')
    search_index = SearchIndex([set(l.strip().split()) for l in tms_lines],
                               similarity_threshold=opt.sss_lambda,
                               similarity_func_name='containment_min')

    print('Building tokenizer...')
    tokenizer = AutoTokenizer.from_pretrained('roberta-large')

    print('Fetching model...')
    model = get_model('roberta-large', 17, False)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model.to(device)

    res = {}
    i = 0
    print('Starting matching ...')
    for src_line in tqdm(src_lines, mininterval=1.0, ncols=50):
        cand_is = match_fuzzy(src_line, search_index, opt)
        if len(cand_is) == 0:
            res[i] = []
        else:
            cand_info = calc_bert_score(src_line, tms_lines, cand_is, model, tokenizer, opt, idf_dict=idf_dict)
            res[i] = cand_info

        i += 1

    print(f'Writing match file to {opt.output}...')
    fw = open(opt.output, 'w')
    for src_i in sorted(res):
        match_line = ' ||| '.join([f'{i} {v}' for v,i in res[src_i]])
        fw.write(f'{match_line}\n')
    fw.close()

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--src', required=True)
    parser.add_argument('-tms', required=True)
    parser.add_argument('-o', '--output', required=True)

    parser.add_argument('--idf-dict', default='tm_idf_dict.en.pt',
                        help='DEFAULT: tm_idf_dict.en.pt')
    parser.add_argument('--sss-lambda', type=float, default=0.5,
                        help='DEFAULT: 0.5')
    parser.add_argument('--sss-nbest', type=int, default=2000,
                        help='DEFAULT: 2000')
    parser.add_argument('--topk', type=int, default=3,
                        help='DEFAULT: 3')
    parser.add_argument('--batch-size', type=int, default=128,
                        help='DEFAULT: 128')

    parser.add_argument('--include-perfect-match', action='store_true', default=False)

    parser.add_argument('--verbose', action='store_true', default=False)

    opt = parser.parse_args()

    process(opt)

if __name__ == '__main__':
    main()