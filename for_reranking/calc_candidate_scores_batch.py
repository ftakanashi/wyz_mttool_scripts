#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def run(cmd):
    print(cmd)
    os.system(cmd)


def preprocess(opt):
    SRC = opt.src
    TGT = opt.tgt
    FAIRSEQ = opt.fairseq_dir
    SCRIPT_TOOL = opt.tool_script_dir
    # N = opt.repeat_number
    beams = [int(p.split('-')[0]) for p in opt.len_opt.split(',')]
    bests = [int(p.split('-')[1]) for p in opt.len_opt.split(',')]
    lenpens = [float(l) for l in opt.lenpen_opt.split(',')]

    data_subdirs = ['{}-{}'.format(SRC, TGT), '{}.rev-{}'.format(SRC, TGT), '{}-{}.rev'.format(SRC, TGT)]
    data_subdirs = [os.path.join(opt.data_dir, d) for d in data_subdirs]
    for d in data_subdirs:
        os.makedirs(d, exist_ok=True)

    # arrange data
    for best in bests:
        for lp in lenpens:
            print(f'Arranging {best}-lp{lp}')
            hyp_fn = os.path.join(opt.hyps_dir, f'hyp.{best}.lp{lp}.{TGT}')
            run('python {}/expand_data_in_row_direction.py -n {} -i {} -o {}'.format(SCRIPT_TOOL, best, opt.source_ref,
                                                                                     os.path.join(data_subdirs[0],
                                                                                                  'test.{}.lp{}.{}'.format(
                                                                                                      best, lp, SRC))))

            run('python {}/expand_data_in_row_direction.py -n {} -i {} -o {}'.format(SCRIPT_TOOL, best, opt.source_ref,
                                                                                     os.path.join(data_subdirs[2],
                                                                                                  'test.{}.lp{}.{}'.format(
                                                                                                      best, lp, SRC))))

            run('python {}/reverse_every_row.py < {} > {}'.format(SCRIPT_TOOL, os.path.join(data_subdirs[0],
                                                                                            'test.{}.lp{}.{}'.format(
                                                                                                best, lp, SRC)),
                                                                  os.path.join(data_subdirs[1],
                                                                               'test.{}.lp{}.{}'.format(best, lp,
                                                                                                        SRC))))

            run('cp {} {}'.format(hyp_fn, os.path.join(data_subdirs[0], 'test.{}.lp{}.{}'.format(best, lp, TGT))))
            run('cp {} {}'.format(hyp_fn, os.path.join(data_subdirs[1], 'test.{}.lp{}.{}'.format(best, lp, TGT))))
            run('python {}/reverse_every_row.py < {} > {}'.format(SCRIPT_TOOL, hyp_fn,
                                                                  os.path.join(data_subdirs[2],
                                                                               'test.{}.lp{}.{}'.format(best, lp,
                                                                                                        TGT))))

    # preprocess
    if not os.path.isfile(os.path.join(opt.data_bin_dir, 'dict.{}.txt'.format(SRC))) or \
            not os.path.isfile(os.path.join(opt.data_bin_dir, 'dict.{}.txt'.format(TGT))):
        raise Exception('You need to prepare a dict file in advance.')

    for best in bests:
        for lp in lenpens:
            data_bin_subdirs = []
            for lang in ('{}2{}'.format(SRC, TGT), '{}2{}'.format(TGT, SRC)):
                for dirc in ('l2r', 'r2l'):
                    data_bin_subdirs.append(f'{lang}.{best}.lp{lp}.{dirc}')

            data_bin_subdirs = [os.path.join(opt.data_bin_dir, d) for d in data_bin_subdirs]
            for d in data_bin_subdirs:
                os.makedirs(d, exist_ok=True)

            proto_cmd = 'python {}/preprocess.py ' \
                        '--source-lang {} --target-lang {} --destdir {} ' \
                        '--workers 64 --testpref {} --srcdict {} --tgtdict {}'
            run(proto_cmd.format(FAIRSEQ, SRC, TGT, data_bin_subdirs[0],
                                 os.path.join(data_subdirs[0], f'test.{best}.lp{lp}'),
                                 os.path.join(opt.data_bin_dir, 'dict.{}.txt'.format(SRC)),
                                 os.path.join(opt.data_bin_dir, 'dict.{}.txt'.format(TGT))))
            run(proto_cmd.format(FAIRSEQ, SRC, TGT, data_bin_subdirs[1],
                                 os.path.join(data_subdirs[2], f'test.{best}.lp{lp}'),
                                 os.path.join(opt.data_bin_dir, 'dict.{}.txt'.format(SRC)),
                                 os.path.join(opt.data_bin_dir, 'dict.{}.txt'.format(TGT))))
            run(proto_cmd.format(FAIRSEQ, TGT, SRC, data_bin_subdirs[2],
                                 os.path.join(data_subdirs[0], f'test.{best}.lp{lp}'),
                                 os.path.join(opt.data_bin_dir, 'dict.{}.txt'.format(TGT)),
                                 os.path.join(opt.data_bin_dir, 'dict.{}.txt'.format(SRC))))
            run(proto_cmd.format(FAIRSEQ, TGT, SRC, data_bin_subdirs[3],
                                 os.path.join(data_subdirs[1], f'test.{best}.lp{lp}'),
                                 os.path.join(opt.data_bin_dir, 'dict.{}.txt'.format(TGT)),
                                 os.path.join(opt.data_bin_dir, 'dict.{}.txt'.format(SRC))))


def calc_score(opt):
    SRC = opt.src
    TGT = opt.tgt
    SCRIPT_TOOL = opt.tool_script_dir
    FAIRSEQ = opt.fairseq_dir
    # N = opt.repeat_number
    bests = [int(p.split('-')[1]) for p in opt.len_opt.split(',')]
    lenpens = [float(l) for l in opt.lenpen_opt.split(',')]
    res_dir = os.path.join(BASE_DIR, 'res')
    if not os.path.isdir(res_dir):
        os.makedirs(res_dir, exist_ok=True)

    categories = []
    for lang_pair in ('{}2{}'.format(SRC, TGT), '{}2{}'.format(TGT, SRC)):
        for dirc in ('l2r', 'r2l'):
            categories.append('{}.{}'.format(lang_pair, dirc))

    def ensemble_model_str(model_dir, cate):
        models = os.listdir(os.path.join(opt.model_dir, cate))
        return ':'.join([os.path.join(model_dir, cate, m) for m in models])

    # calculate reference score
    proto_cmd = 'python {}/generate.py {} --path {} --max-sentences 128 --score-reference | tee {}'
    for best in bests:
        for lp in lenpens:
            for category in categories:
                lang, dirc = category.split('.')
                data_bin_dir = os.path.join(opt.data_bin_dir, f'{lang}.{best}.lp{lp}.{dirc}')
                generate_log_fn = os.path.join(res_dir, f'{lang}.{best}.lp{lp}.{dirc}.generate.log')
                score_fn = os.path.join(res_dir, f'{lang}.{best}.lp{lp}.{dirc}.score')
                run(proto_cmd.format(FAIRSEQ, data_bin_dir, ensemble_model_str(opt.model_dir, category), generate_log_fn))
                run('python {}/for_reranking/extract_score.py < {} > {}'.format(SCRIPT_TOOL, generate_log_fn, score_fn))

            if opt.add_word_ratio:
                if opt.std_ratio < 0:
                    raise Exception('Specify the standard ratio.')

                # unbpe
                src_fn = os.path.join(opt.data_dir, f'{SRC}-{TGT}', f'test.{best}.lp{lp}.{SRC}')
                hyp_fn = os.path.join(opt.data_dir, f'{SRC}-{TGT}', f'test.{best}.lp{lp}.{TGT}')
                run(f'python {SCRIPT_TOOL}/remove_bpe.py < {src_fn} > .src.unbpe.tmp')
                run(f'python {SCRIPT_TOOL}/remove_bpe.py < {hyp_fn} > .hyp.unbpe.tmp')

                # calc word_ratio
                output_fn = os.path.join(res_dir, f'word_ratio.{best}.lp{lp}.score')
                run(f'python {SCRIPT_TOOL}/for_reranking/calc_word_ratio.py --src .src.unbpe.tmp --tgt .hyp.unbpe.tmp'
                    f' --std-ratio {opt.std_ratio} --output {output_fn}')

            # concat scores
            score_fns = []
            for category in categories:
                lang, dirc = category.split('.')
                score_fns.append(os.path.join(res_dir, f'{lang}.{best}.lp{lp}.{dirc}.score'))
            concat_cmd = 'paste ' + ' '.join(score_fns)

            if opt.add_word_ratio:
                concat_cmd += ' {}'.format(os.path.join(res_dir, f'word_ratio.{best}.lp{lp}.score'))
            concat_cmd += ' | awk -F \' \' \'{print'
            for i, c in enumerate(categories):
                concat_cmd += ' " {}= "${}'.format(c, i + 1)
            if opt.add_word_ratio:
                concat_cmd += ' " word_ratio= "$5'
            total_score_fn = os.path.join(res_dir, f'total.{best}.lp{lp}.score')
            concat_cmd += '}}\' > {}'.format(total_score_fn)

            run(concat_cmd)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--src', required=True,
                        help='Source Language')
    parser.add_argument('-t', '--tgt', required=True,
                        help='Target Language')
    # parser.add_argument('-n', '--repeat-number', required=True, type=int,
    #                     help='Repeat Number')
    parser.add_argument('-r', '--source-ref', required=True,
                        help='Path to the source corpus file.(Used to expand data in row if n>1)')
    # parser.add_argument('-p', '--hyp', required=True,
    #                     help='Path to the hypothesis file.')
    parser.add_argument('--hyps-dir', required=True,
                        help='Path to the dir where all hypothesis files are saved.')

    parser.add_argument('--model-dir', default=os.path.join(BASE_DIR, 'model'),
                        help='Path to the model dir')
    parser.add_argument('--fairseq-dir', default=os.path.join(BASE_DIR, 'fairseq'),
                        help='Path to the fairseq dir.')
    parser.add_argument('--tool-script-dir', default=os.path.join(BASE_DIR, 'wyz_mttool_scripts'),
                        help='Path to the tool script dir')
    parser.add_argument('--data-dir', default=os.path.join(BASE_DIR, 'data'))
    parser.add_argument('--data-bin-dir', default=os.path.join(BASE_DIR, 'data-bin'))

    parser.add_argument('--add-word-ratio', action='store_true', default=False)
    parser.add_argument('--std-ratio', default=-1, type=float)

    parser.add_argument('--len-opt', required=True, help='Length options used when running generate_nbest.py')
    parser.add_argument('--lenpen-opt', required=True, help='Lenpen options used when running generate_nbest.py')

    opt = parser.parse_args()

    if opt.add_word_ratio and opt.std_ratio == -1:
        raise Exception('standard ratio should be specified.')

    preprocess(opt)
    calc_score(opt)


if __name__ == '__main__':
    main()
