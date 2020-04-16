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
    # N = opt.repeat_number
    SCRIPT_TOOL = opt.tool_script_dir
    SCORE_LOG = opt.score_log_dir
    MOSES = opt.moses_script_dir

    TMP = os.path.join(BASE_DIR, 'tmp')
    os.makedirs(TMP, exist_ok=True)

    RESCORED_HYP_DIR = os.path.join(BASE_DIR, 'rescored_hyps')
    os.makedirs(RESCORED_HYP_DIR, exist_ok=True)

    bests = [int(p.split('-')[1]) for p in opt.len_opt.split(',')]
    lenpens = [float(l) for l in opt.lenpen_opt.split(',')]

    for best in bests:
        for lp in lenpens:

            hyp_fn = os.path.join(opt.hyps_dir, f'hyp.{best}.lp{lp}.{TGT}')
            total_score_fn = os.path.join(SCORE_LOG, f'total.{best}.lp{lp}.score')
            origin_score_fn = os.path.join(SCORE_LOG, f'{SRC}2{TGT}.{best}.lp{lp}.l2r.score')
            # generate nbest training file
            with_features_fn = os.path.join(TMP, f'hyp.with-features.{best}.lp{lp}.{TGT}')
            run(f'python {SCRIPT_TOOL}/for_reranking/generate_nbest_train_file.py -n {best} --hyp {hyp_fn} '
                f'--total-score {total_score_fn} --origin-score {origin_score_fn} --output {with_features_fn}')

            # train
            working_dir = os.path.join(BASE_DIR,'rescore-work', f'rescore-work.{best}.lp{lp}')
            run('python {}/train.py --nbest {} --ref {} --working-dir {}'.format(
                MOSES, with_features_fn, opt.ref, working_dir))

            # rename rescore.ini
            # run('mv {}/rescore.ini {}/rescore.{}.ini'.format(working_dir, working_dir, N))

            # rescore with-features
            rescored_with_features_fn = os.path.join(TMP, f'hyp.with-features.rescored.{best}.lp{lp}.{TGT}')
            run('python {}/rescore.py {} < {} > {}'.format(
                MOSES, os.path.join(working_dir, 'rescore.ini'),
                    with_features_fn, rescored_with_features_fn))

            # decode
            rescored_hyp_fn = os.path.join(RESCORED_HYP_DIR, f'hyp.rescored.{best}.lp{lp}.{TGT}')
            run('python {}/topbest.py < {} > {}'.format(
                MOSES, rescored_with_features_fn, rescored_hyp_fn
            ))

    # remove tmp dir
    run('rm -rf {}'.format(TMP))

def calc_bleu(opt):
    TGT = opt.tgt
    # N = opt.repeat_number
    SCRIPT_TOOL = opt.tool_script_dir

    RESCORED_HYP_DIR = os.path.join(BASE_DIR, 'rescored_hyps')
    os.makedirs(RESCORED_HYP_DIR, exist_ok=True)
    CALC_BLEU_DIR = os.path.join(BASE_DIR, 'rescored_hyps', 'calc_bleu')
    os.makedirs(CALC_BLEU_DIR, exist_ok=True)
    BLEU_RES_DIR = os.path.join(BASE_DIR, 'rescored_hyps', 'bleu_res')
    os.makedirs(BLEU_RES_DIR, exist_ok=True)

    MOSES = os.path.dirname(opt.moses_script_dir)
    MOSES = os.path.join(MOSES, 'generic', 'multi-bleu.perl')

    bests = [int(p.split('-')[1]) for p in opt.len_opt.split(',')]
    lenpens = [float(l) for l in opt.lenpen_opt.split(',')]

    for best in bests:
        for lp in lenpens:
            hyp_fn = os.path.join(RESCORED_HYP_DIR, f'hyp.rescored.{best}.lp{lp}.{TGT}')
            hyp_ch_fn = os.path.join(CALC_BLEU_DIR, f'hyp.rescored.ch.{best}.lp{lp}.{TGT}')
            run(f'python {SCRIPT_TOOL}/remove_bpe.py < {hyp_fn} | python {SCRIPT_TOOL}/split_into_char.py > {hyp_ch_fn}')

            ref_ch_fn = os.path.join(CALC_BLEU_DIR, 'ref.ch.{}'.format(TGT))
            run(f'python {SCRIPT_TOOL}/remove_bpe.py < opt.ref | python {SCRIPT_TOOL}/split_into_char.py > {ref_ch_fn}')

            run(f'perl {MOSES} {ref_ch_fn} < {hyp_ch_fn} > {BLEU_RES_DIR}/bleu.{best}.lp{lp}')

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--src', required=True,
                        help='Source Language')
    parser.add_argument('-t', '--tgt', required=True,
                        help='Target Language')
    # parser.add_argument('-n', '--repeat-number', required=True, type=int,
    #                     help='Repeat Number')
    parser.add_argument('-r', '--ref', required=True,
                        help='Path to the reference file.')
    # parser.add_argument('-p', '--hyp', required=True,
    #                     help='Path to the hypothesis file.')
    parser.add_argument('--hyps-dir', required=True,
                        help='Path to the directory where hyps are saved.')

    parser.add_argument('--score-log-dir', required=True,
                        help='Path to the score log dir where total.score and other scores are saved.')

    parser.add_argument('--moses-script-dir', default='../../mosesdecoder/scripts/nbest-rescore')
    parser.add_argument('--tool-script-dir', default='../wyz_mttool_scripts')

    parser.add_argument('--len-opt', required=True, help='Length options used when running generate_nbest.py')
    parser.add_argument('--lenpen-opt', required=True, help='Lenpen options used when running generate_nbest.py')

    opt = parser.parse_args()

    train_and_decode(opt)

    calc_bleu(opt)

if __name__ == '__main__':
    main()