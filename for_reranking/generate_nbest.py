#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run(cmd):
    print(cmd)
    os.system(cmd)

def generate(opt):
    SRC = opt.src
    TGT = opt.tgt
    SCRIPT_TOOL = opt.tool_script_dir

    lengths = opt.len_opt.split(',')

    beam_len = [l.split('-')[0] for l in lengths]
    best_len = [l.split('-')[1] for l in lengths]

    def ensemble_model_str(model_dir, cate):
        models = [f for f in os.listdir(os.path.join(opt.model_dir, cate)) if os.path.splitext(f)[1] == '.pt']
        return ':'.join([os.path.join(model_dir, cate, m) for m in models])

    # generate and clean the log
    for beam,best in zip(beam_len, best_len):
        log_fn = 'generate.{}.log'.format(best)
        cmd = 'python fairseq/generate.py {} --path {} --beam {} --nbest {}'.format(
            opt.data_bin_dir, ensemble_model_str(opt.model_dir, '{}2{}.l2r'.format(SRC, TGT)),
            beam, best
        )
        if opt.max_tokens is not None and opt.max_tokens > 0:
            cmd += ' --max-tokens {}'.format(opt.max_tokens)
        elif opt.max_sentences is not None and opt.max_sentences > 0:
            cmd += ' --max-sentences {}'.format(opt.max_sentences)
        else:
            raise Exception('Invalid mini-batch size.')

        cmd += ' | tee {}'.format(log_fn)
        run(cmd)

        hyp_fn = 'hyp.{}.{}'.format(best, TGT)
        run('python {}/extract_hyp_wei.py -i {} -o {} -n {}'.format(SCRIPT_TOOL, log_fn, hyp_fn, best))
        if not opt.retain_log:
            run('rm -f {}'.format(log_fn))


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--src', required=True,
                        help='Source Language')
    parser.add_argument('-t', '--tgt', required=True,
                        help='Target Language')

    parser.add_argument('--len-opt', required=True,
                        help='Length options. Like: 5-5,10-10,25-20')
    parser.add_argument('--model-dir', required=True,
                        help='Path to the model dir.')

    parser.add_argument('--data-bin-dir', default='data-bin',
                        help='Path to the data-bin.')
    parser.add_argument('--max-tokens', type=int,
                        help='Specify max tokens in a mini-batch.')
    parser.add_argument('--max-sentences', type=int,
                        help='Specify max sentences in a mini-batch')

    parser.add_argument('--tool-script-dir', default=os.path.join(BASE_DIR, 'wyz_mttool_scripts'))
    parser.add_argument('--retain-log', action='store_true', default=False)

    opt = parser.parse_args()

    if opt.max_tokens is None and opt.max_sentences is None:
        raise Exception('You must select max-tokens or max-sentences to limit the size of mini-batches.')

    generate(opt)


if __name__ == '__main__':
    main()