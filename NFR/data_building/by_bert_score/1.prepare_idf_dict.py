#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import pickle
import time
from transformers import AutoTokenizer
from bert_score.bert_score.utils import get_idf_dict

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input', required=True)
    parser.add_argument('-n', '--nthreads', type=int, default=4)
    parser.add_argument('-o', '--output', default='idf_dict.pt')

    opt = parser.parse_args()

    start = time.time()

    print('Reading source file..')
    with open(opt.input, 'r') as f:
        refs = [l.strip() for l in f]

    print('Building idf dictionary...')
    idf_dict = get_idf_dict(refs, AutoTokenizer.from_pretrained('roberta-large'), nthreads=opt.nthreads)
    default_v = idf_dict['____']
    idf_dict = dict(idf_dict)
    idf_dict['default_value'] = default_v

    fw = open(opt.output, 'wb')
    pickle.dump(idf_dict, fw)
    fw.close()

    end = time.time()
    print(f'Time consumed: {end - start} seconds...')

if __name__ == '__main__':
    main()
