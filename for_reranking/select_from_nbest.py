#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run(cmd):
    print(cmd)
    os.system(cmd)

def make_feature_file_and_rescore(opt):
    SRC = opt.src
    TGT = opt.tgt
    N = opt.repeat_number
    MOSES = opt.moses_script_dir
    SCRIPT_TOOL = opt.tool_script_dir

    # make with-feature file
    with_feature_fn = os.path.join(opt.score_log_dir, 'hyp.with-features.{}.{}'.format(N, TGT))
    run('python {}/for_reranking/generate_nbest_train_file.py -n {} --hyp {} --total-score {} --origin-score {}'
        ' --output {}'.format(
        SCRIPT_TOOL, N, opt.hyp,
        os.path.join(opt.score_log_dir, 'total.score'),
        os.path.join(opt.score_log_dir, '{}2{}.l2r.score'.format(SRC, TGT)),
        with_feature_fn
    ))

    # rescore with-feature file
    rescored_with_feature_fn = os.path.join(opt.score_log_dir, 'hyp.with-features.rescored.{}.{}'.format(N, TGT))
    run('python {}/rescore.py {} < {} > {}'.format(
        MOSES, opt.rescore_ini, with_feature_fn, rescored_with_feature_fn
    ))

    # decode rescored with-feature file
    reranked_hyp_fn = 'hyp.reranked.{}.{}'.format(N, TGT)
    run('python {}/topbest.py < {} > {}'.format(
        MOSES, rescored_with_feature_fn, reranked_hyp_fn
    ))

    # post edit
    run('python {}/for_reranking/post_edit.py -t {} -i {} -o {} --tool-script-dir {}'.format(
        SCRIPT_TOOL, TGT, reranked_hyp_fn, 'hyp.final.{}'.format(TGT), SCRIPT_TOOL
    ))


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--src', required=True,
                        help='Source language')
    parser.add_argument('-t', '--tgt', required=True,
                        help='Target language')
    parser.add_argument('-n', '--repeat-number', required=True, type=int,
                        help='Repeat Number')
    parser.add_argument('-p', '--hyp', required=True,
                        help='Hypothesis file')
    parser.add_argument('--score-log-dir', required=True,
                        help='Path to the score log dir')
    parser.add_argument('--rescore-ini', required=True,
                        help='Path to the rescore.ini')

    parser.add_argument('--moses-script-dir', default='/root/work/smt/mosesdecoder/scripts/nbest-rescore')
    parser.add_argument('--tool-script-dir', default=os.path.join(BASE_DIR, 'wyz_mttool_scripts'))

    parser.add_argument('--post-edit', type='store_true', default=False, help='Whether to do postedit.')

    opt = parser.parse_args()

    make_feature_file_and_rescore(opt)

if __name__ == '__main__':
    main()