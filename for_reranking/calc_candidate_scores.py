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
    SCRIPT_TOOL = opt.tool_script_dir
    N = opt.repeat_number

    data_subdirs = ['{}-{}'.format(SRC, TGT), '{}.rev-{}'.format(SRC, TGT), '{}-{}.rev'.format(SRC, TGT)]
    data_subdirs = [os.path.join(opt.data_dir, d) for d in data_subdirs]
    for d in data_subdirs:
        os.makedirs(d, exist_ok=True)

    # arrange data
    run('python {}/expand_data_in_row_direction.py -n {} -i {} -o {}'.format(SCRIPT_TOOL, N, opt.source_ref,
        os.path.join(data_subdirs[0], 'test.{}.{}'.format(N, SRC))))
    run('python {}/expand_data_in_row_direction.py -n {} -i {} -o {}'.format(SCRIPT_TOOL, N, opt.source_ref,
        os.path.join(data_subdirs[2], 'test.{}.{}'.format(N, SRC))))
    run('python {}/reverse_every_row.py < {} > {}'.format(SCRIPT_TOOL, os.path.join(data_subdirs[0], 'test.{}.{}'.format(N, SRC)),
        os.path.join(data_subdirs[1], 'test.{}.{}'.format(N, SRC))))

    run('cp {} {}'.format(opt.hyp, os.path.join(data_subdirs[0], 'test.{}.{}'.format(N, TGT))))
    run('cp {} {}'.format(opt.hyp, os.path.join(data_subdirs[1], 'test.{}.{}'.format(N, TGT))))
    run('python {}/reverse_every_row.py < {} > {}'.format(SCRIPT_TOOL, opt.hyp,
        os.path.join(data_subdirs[2], 'test.{}.{}'.format(N, TGT))))

    # preprocess
    data_bin_subdirs = []
    for lang in ('{}2{}'.format(SRC, TGT), '{}2{}'.format(TGT, SRC)):
        for dirc in ('l2r', 'r2l'):
            data_bin_subdirs.append('{}.{}'.format(lang, dirc))
    data_bin_subdirs = [os.path.join(opt.data_bin_dir, d) for d in data_bin_subdirs]
    for d in data_bin_subdirs:
        os.makedirs(d, exist_ok=True)

    proto_cmd = 'python fairseq/preprocess.py ' \
                '--source-lang {} --target-lang {} --destdir {} ' \
                '--workers 64 --testpref {} --srcdict {} --tgtdict {}'
    run(proto_cmd.format(SRC, TGT, data_bin_subdirs[0],
                         os.path.join(data_subdirs[0], 'test.{}'.format(N)),
                         os.path.join(opt.data_bin_dir, 'dict.{}.txt'.format(SRC)),
                         os.path.join(opt.data_bin_dir, 'dict.{}.txt'.format(TGT))))
    run(proto_cmd.format(SRC, TGT, data_bin_subdirs[1],
                         os.path.join(data_subdirs[2], 'test.{}'.format(N)),
                         os.path.join(opt.data_bin_dir, 'dict.{}.txt'.format(SRC)),
                         os.path.join(opt.data_bin_dir, 'dict.{}.txt'.format(TGT))))
    run(proto_cmd.format(TGT, SRC, data_bin_subdirs[2],
                         os.path.join(data_subdirs[0], 'test.{}'.format(N)),
                         os.path.join(opt.data_bin_dir, 'dict.{}.txt'.format(TGT)),
                         os.path.join(opt.data_bin_dir, 'dict.{}.txt'.format(SRC))))
    run(proto_cmd.format(TGT, SRC, data_bin_subdirs[3],
                         os.path.join(data_subdirs[1], 'test.{}'.format(N)),
                         os.path.join(opt.data_bin_dir, 'dict.{}.txt'.format(TGT)),
                         os.path.join(opt.data_bin_dir, 'dict.{}.txt'.format(SRC))))

def calc_score(opt):
    SRC = opt.src
    TGT = opt.tgt
    SCRIPT_TOOL = opt.tool_script_dir
    N = opt.repeat_number
    result_dir = os.path.join(BASE_DIR, 'score_log.{}best'.format(N))

    categories = []
    for lang_pair in ('{}2{}'.format(SRC, TGT), '{}2{}'.format(TGT, SRC)):
        for dirc in ('l2r', 'r2l'):
            categories.append('{}.{}'.format(lang_pair, dirc))

    proto_cmd = 'python fairseq/generate.py {} --path {} --max-sentences 64 --score-reference | tee {}'

    def ensemble_model_str(model_dir, cate):
        models = os.listdir(os.path.join(opt.model_dir, cate))
        return ':'.join([os.path.join(model_dir, cate, m) for m in models])

    for category in categories:
        run(proto_cmd.format(os.path.join(opt.data_bin_dir, category),
                             ensemble_model_str(opt.model_dir, category),
                             os.path.join(result_dir, category+'.generate.log')))
        run('python {}/for_reranking/extract_score.py < {} > {}'.format(SCRIPT_TOOL,
                                                                        os.path.join(result_dir, category+'.generate.log'),
                                                                        os.path.join(result_dir, category+'.score')))

    if opt.add_word_ratio:
        if opt.std_ratio < 0:
            raise Exception('Specify the standard ratio.')
        run('python {}/for_reranking/calc_word_ratio.py --src {} --tgt {} --std-ratio {} --output {}'.format(
            SCRIPT_TOOL, opt.source_ref, opt.hyp, opt.std_ratio, os.path.join(result_dir, 'word_ratio.score')
        ))

    # concat scores
    concat_cmd = 'paste ' + ' '.join([os.path.join(result_dir, c+'.score') for c in categories])
    if opt.add_word_ratio:
        concat_cmd += ' {}'.format(os.path.join(result_dir, 'word_ratio.score'))
    concat_cmd += ' | awk -F \' \' \'{print'
    for i,c in enumerate(categories):
        concat_cmd += ' "{}= "${}'.format(c, i+1)
    if opt.add_word_ratio:
        concat_cmd += ' "word_ratio= "$5'
    concat_cmd += '}}\' > {}'.format(os.path.join(result_dir, 'total.score'))

    run(concat_cmd)

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--src', required=True,
                        help='Source Language')
    parser.add_argument('-t', '--tgt', required=True,
                        help='Target Language')
    parser.add_argument('-n', '--repeat-number', required=True, type=int,
                        help='Repeat Number')
    parser.add_argument('-r', '--source-ref', required=True,
                        help='Path to the source reference file.')
    parser.add_argument('-p', '--hyp', required=True,
                        help='Path to the hypothesis file.')

    parser.add_argument('--model-dir', default=os.path.join(BASE_DIR, 'model'),
                        help='Path to the model dir')
    parser.add_argument('--tool-script-dir', default=os.path.join(BASE_DIR, 'wyz_mttool_scripts'),
                        help='Path to the tool script dir')
    parser.add_argument('--data-dir', default=os.path.join(BASE_DIR, 'data'))
    parser.add_argument('--data-bin-dir', default=os.path.join(BASE_DIR, 'data-bin'))

    parser.add_argument('--add-word-ratio', action='store_true', default=False)
    parser.add_argument('--std-ratio', default=-1, type=float)

    opt = parser.parse_args()

    preprocess(opt)
    calc_score(opt)


if __name__ == '__main__':
    main()