#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse

def transfer_alignment(align_line, src_len):
    '''
    由fast_align得到的alignment文件可能会出现某位置src无对应
    这个函数用来修正（两种情况，如果缺失位置是句首则对应到-1  例：2 - 1 ...(0,1缺失) 变成 0 - -1  1 - -1  2 - 1 ...
    如果是中间位置缺失，则沿用前一个对应关系的tgt侧，例：3-3 5-5 ... (缺失4) 变成 3-3 4-3 5-5 ...
    :param align_line:
    :param src_len:
    :return:
    '''
    align_pairs = align_line.strip().split()
    s_align, t_align = [], []
    for pair in align_pairs:
        s, t = pair.split('-')
        s = int(s)
        t = int(t)
        s_align.append(s)
        t_align.append(t)

    origin_alignments = list(zip(s_align, t_align))
    addition_alignments = []
    last_t_align = -1
    for src_i in range(src_len):
        if src_i not in s_align:
            addition_alignments.append((src_i, last_t_align))
        else:
            last_t_align = t_align[s_align.index(src_i)]

    origin_alignments.extend(addition_alignments)
    return list(sorted(origin_alignments, key=lambda x: x[0]))


def process(src_line, tgt_line, align_line, dummy_token):
    '''
    将输入的一行src一行tgt以及一行alignment进行整合
    输出的container是个tuple的list，每个tuple有两个元素:(部分source文，根据alignment对应出来的部分译文)
    :param src_line:
    :param tgt_line:
    :param align_line:
    :param dummy_token:
    :return:
    '''
    src_tokens = src_line.strip().split()
    src_len = len(src_tokens)
    tgt_tokens = tgt_line.strip().split()
    alignments = transfer_alignment(align_line, src_len)

    container = []
    partial_t_tokens = []

    for s_i, t_i in alignments:
        if t_i == -1:
            continue
        src_str = ' '.join(src_tokens[:s_i+1])
        if t_i+1 > len(partial_t_tokens):
            for _ in range(t_i-len(partial_t_tokens)):
                partial_t_tokens.append(dummy_token)
            partial_t_tokens.append(tgt_tokens[t_i])
        else:
            partial_t_tokens[t_i] = tgt_tokens[t_i]
        tgt_str = ' '.join(partial_t_tokens)
        container.append((src_str, tgt_str))

    return container

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-src', required=True,
                        help='Path to the source file.')
    parser.add_argument('-tgt', required=True,
                        help='Path to the target file.')
    parser.add_argument('-align',  required=True,
                        help='Path to the align file.')
    parser.add_argument('-dummy-token', default='[DUMMY]',
                        help='specify the representation of a dummy token.')

    opt = parser.parse_args()
    f_src = open(opt.src, 'r')
    f_tgt = open(opt.tgt, 'r')
    f_align = open(opt.align, 'r')
    f_src_new = open('{}.new'.format(opt.src), 'w')
    f_tgt_new = open('{}.new'.format(opt.tgt), 'w')

    src_lines = f_src.readlines()
    tgt_lines = f_tgt.readlines()
    align_lines = f_align.readlines()

    assert len(src_lines) == len(tgt_lines)
    assert len(src_lines) == len(align_lines)

    for i,src_line in enumerate(src_lines):
        tgt_line = tgt_lines[i]
        align_line = align_lines[i]
        container = process(src_line, tgt_line, align_line, opt.dummy_token)
        for s_str, t_str in container:
            f_src_new.write('{}\n'.format(s_str.strip()))
            f_tgt_new.write('{}\n'.format(t_str.strip()))

        f_src_new.write(src_line.strip() + '\n')    # 为了防止中间有些tgt token从都是DUMMY，进行补全
        f_tgt_new.write(tgt_line.strip() + '\n')

    f_src.close(), f_tgt.close(), f_align.close()
    f_src_new.close(), f_tgt_new.close()

if __name__ == '__main__':
    main()