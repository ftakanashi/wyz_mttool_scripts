#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
Counting sentence-bleu for every sentence between two files. Number of rows in two files should match.
'''

import argparse
import codecs

from nltk.translate.bleu_score import sentence_bleu

def calc_sent_bleu(opt):
    ref_f = codecs.open(opt.reference, 'r', encoding=opt.encoding)
    hyp_f = codecs.open(opt.hypothesis, 'r', encoding=opt.encoding)
    ref_lines = ref_f.readlines()
    hyp_lines = hyp_f.readlines()
    ref_f.close()
    hyp_f.close()

    assert len(ref_lines) == len(hyp_lines), 'Number of Rows Does not Match.'

    sent_bleus = []
    for r,h in zip(ref_lines, hyp_lines):
        sent_bleus.append(sentence_bleu(r.split(), h.split()))

    return ref_lines, hyp_lines, sent_bleus

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-r', '--reference', required=True,
                        help='Path to the reference file.')
    parser.add_argument('-h', '--hypothesis', required=True,
                        help='Path to the hypothesis file.')
    parser.add_argument('-o', '--output', required=True,
                        help='Path to the output file.')
    parser.add_argument('-e', '--encoding', default='utf-8',
                        help='Specify the codecs to read/write file.')
    parser.add_argument('--output-format', default='full',
                        help='Content format to output. Options are [full, simple]')

    opt = parser.parse_args()

    if opt.output_format not in ('full', 'simple'):
        raise Exception('Invalid output format {}.'.format(opt.output_format))

    ref_lines, hyp_lines, sent_bleus = calc_sent_bleu(opt)
    wf = codecs.open(opt.output, 'w', encoding=opt.encoding)
    if opt.output_format == 'full':
        for r,h,b in zip(ref_lines, hyp_lines, sent_bleus):
            wf.write('\t'.join((r,h,str(b))))
    elif opt.output_format == 'simple':
        for b in sent_bleus:
            wf.write(str(b))
    wf.close()

if __name__ == '__main__':
    print('Please make sure that your file is already tokenized.')
    import time
    time.sleep(1)
    main()