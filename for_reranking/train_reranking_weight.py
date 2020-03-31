#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run(cmd):
    print(cmd)
    os.system(cmd)

def train_and_decode(opt):
    SRC = opt.src
    TGT = opt.tgt
    N = opt.repeat_number
    SCRIPT_TOOL = opt.tool_script_dir
    SCORE_LOG = opt.score_log_dir
    MOSES = opt.moses_script_dir

    TMP = os.path.join(BASE_DIR, 'tmp')
    os.makedirs(TMP, exist_ok=True)

    # generate nbest training file
    with_features_fn = os.path.join(TMP, 'hyp.with-features.{}.{}'.format(N, TGT))
    run('python {}/for_reranking/generate_nbest_train_file.py -n {} --hyp {} --total-score {} --origin-score {}'
        ' --output {}'.format(
        SCRIPT_TOOL, N, opt.hyp, os.path.join(SCORE_LOG, 'total.score'),
            os.path.join(SCORE_LOG, '{}2{}.l2r.score'.format(SRC, TGT)), with_features_fn))

    # train
    working_dir = os.path.join(BASE_DIR, 'rescore-work.{}'.format(N))
    run('python {}/train.py --nbest {} --ref {} --working-dir {}'.format(
        MOSES, with_features_fn, opt.ref, working_dir))

    # rename rescore.ini
    run('mv {}/rescore.ini {}/rescore.{}.ini'.format(working_dir, working_dir, N))

    # rescore with-features
    rescored_with_features_fn = os.path.join(TMP, 'hyp.with-features.{}.rescored.{}'.format(N, TGT))
    run('python {}/rescore.py {} < {} > {}'.format(
        MOSES, os.path.join(working_dir, 'rescore.{}.ini'.format(N), with_features_fn,
                            rescored_with_features_fn)
    ))

    # decode
    run('python {}/topbest.py < {} > {}'.format(
        MOSES, rescored_with_features_fn, 'hyp.rescored.{}.{}'.format(N, TGT)
    ))

    # remove tmp dir
    run('rm -rf {}'.format(TMP))

def calc_bleu(opt):
    TGT = opt.tgt
    N = opt.repeat_number
    SCRIPT_TOOL = opt.tool_script_dir
    TMP = os.path.join(BASE_DIR, 'calc-bleu')
    os.makedirs(TMP, exist_ok=True)

    MOSES = os.path.dirname(opt.moses_dir)
    MOSES = os.path.join(MOSES, 'generic', 'multi-bleu.perl')

    hyp_fn = os.path.join(TMP, 'hyp.{}'.format(TGT))
    hyp_ch_fn = os.path.join(TMP, 'hyp.ch.{}'.format(TGT))
    run('python {}/remove_bpe.py < {} > {}'.format(
        SCRIPT_TOOL, 'hyp.rescored.{}.{}'.format(N, TGT), hyp_fn))
    run('python {}/split_into_char.py < {} > {}'.format(
        SCRIPT_TOOL, hyp_fn, hyp_ch_fn))

    ref_fn = os.path.join(TMP, 'ref.{}'.format(TGT))
    ref_ch_fn = os.path.join(TMP, 'ref.ch.{}'.format(TGT))
    run('python {}/remove_bpe.py < {} > {}'.format(
        SCRIPT_TOOL, opt.ref, ref_fn))
    run('python {}/split_into_char.py < {} > {}'.format(
        SCRIPT_TOOL, ref_fn, ref_ch_fn))

    run('perl {} {} < {}'.format(MOSES, ref_ch_fn, hyp_ch_fn))

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--src', required=True,
                        help='Source Language')
    parser.add_argument('-t', '--tgt', required=True,
                        help='Target Language')
    parser.add_argument('-n', '--repeat-number', required=True, type=int,
                        help='Repeat Number')
    parser.add_argument('-r', '--ref', required=True,
                        help='Path to the reference file.')
    parser.add_argument('-p', '--hyp', required=True,
                        help='Path to the hypothesis file.')

    parser.add_argument('--score-log-dir', required=True,
                        help='Path to the score log dir where total.score and other scores are saved.')

    parser.add_argument('--moses-script-dir', default='/root/work/smt/mosesdecoder/scripts/nbest-rescore')
    parser.add_argument('--tool-script-dir', default=os.path.join(BASE_DIR, 'wyz_mttool_scripts'))

    opt = parser.parse_args()

    train_and_decode(opt)

if __name__ == '__main__':
    main()