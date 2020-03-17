#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse

def fuse_token(tokens, tgt_token):
    # assert len(tokens) > 0
    res = []
    for t in tokens:
        if t == tgt_token and len(res) > 0 and res[-1] == tgt_token:
            continue
        res.append(t)
    return res

def fuse_dummy(opt):
    with open(opt.reference, 'r') as f:
        ref_lines = f.readlines()

    with open(opt.hypothesis, 'r') as f:
        hyp_lines = f.readlines()

    new_ref_fn = '{}.{}'.format(opt.reference, opt.suffix)
    new_hyp_fn = '{}.{}'.format(opt.hypothesis, opt.suffix)

    new_ref = open(new_ref_fn, 'w')
    new_hyp = open(new_hyp_fn, 'w')

    for r,h in zip(ref_lines, hyp_lines):
        r_tokens = r.strip().split()
        h_tokens = h.strip().split()
        r_tokens = fuse_token(r_tokens, opt.token)
        h_tokens = fuse_token(h_tokens, opt.token)
        new_ref.write(' '.join(r_tokens) + '\n')
        new_hyp.write(' '.join(h_tokens) + '\n')

    new_ref.close(), new_hyp.close()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-r', '--reference', required=True,
                        help='Path to the reference file.')
    parser.add_argument('-p', '--hypothesis', required=True,
                        help='Path to the hypothesis file.')
    parser.add_argument('-t', '--token', default='[DUMMY]',
                        help='explicitly specify the token. Default: [DUMMY]')
    parser.add_argument('--suffix', default='fused',
                        help='Specify the suffix of the output file. Default: fused')

    opt = parser.parse_args()

    fuse_dummy(opt)

if __name__ == '__main__':
    main()
