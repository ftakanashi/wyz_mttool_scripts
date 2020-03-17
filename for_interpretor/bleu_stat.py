#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import os
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_PATH = os.path.join(BASE_DIR, 'mosesdecoder', 'scripts', 'generic', 'multi-bleu.perl')

def bleu_stat(opt):
    script_path = opt.bleu_script
    max_len_limit = int(opt.max_len_limit)
    ref_pfx = opt.reference_prefix
    hyp_pfx = opt.hypothesis_prefix
    do_lowercase = opt.lowercase

    cmd_root = 'perl {} '.format(script_path)
    if do_lowercase:
        cmd_root += '-lc '

    for len_cate in range(1, max_len_limit+1):
        print('LENGTH = {}'.format(len_cate))
        ref_fn = '{}.{}'.format(ref_pfx, len_cate)
        hyp_fn = '{}.{}'.format(hyp_pfx, len_cate)
        cmd = '{} {} < {}'.format(cmd_root, ref_fn, hyp_fn)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if err:
            print(str(err, encoding='utf-8'))
        print(str(out, encoding='utf-8'))

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-r', '--reference-prefix', default='ref',
                        help='Specify the reference prefix. Default: ref')
    parser.add_argument('-p', '--hypothesis-prefix', default='hyp',
                        help='Specify the hypothesis prefix. Default: hyp')
    parser.add_argument('-m', '--max-len-limit', type=int, default=20,
                        help='Max length limit.')

    parser.add_argument('--lowercase', action='store_true',
                        help='Calculate BLEU score with lowercase.')
    parser.add_argument('--bleu-script', default=SCRIPT_PATH,
                        help='Path to the BLEU script. Default: {}'.format(SCRIPT_PATH))

    opt = parser.parse_args()
    bleu_stat(opt)


if __name__ == '__main__':
    main()