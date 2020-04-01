#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run(cmd):
    print(cmd)
    os.system(cmd)

def post_edit(opt):
    TGT = opt.tgt
    SCRIPT_TOOL = opt.tool_script_dir

    TMP = os.path.join(BASE_DIR, 'tmp')
    os.makedirs(TMP, exist_ok=True)

    # remove bpe
    run('python {}/remove_bpe.py < {} > {}'.format(
        SCRIPT_TOOL, opt.input, os.path.join(TMP, 'hyp.unbpe.' + TGT)
    ))

    # half char to full
    run('python {}/half_full_char/toggle_full_half.py --mode h2f --toggle-group punctuations --exception \\" '
        '< {} > {}'.format(
        SCRIPT_TOOL, os.path.join(TMP, 'hyp.unbpe.' + TGT), os.path.join(TMP, 'hyp.unbpe.full.' + TGT)
    ))

    # detokenize
    run('python {}/detokenize.py < {} > {}'.format(
        SCRIPT_TOOL,
        os.path.join(TMP, 'hyp.unbpe.full.' + TGT),
        'hyp.final.{}'.format(TGT)
    ))

    run('rm -rf {}'.format(TMP))

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-t', '--tgt', required=True,
                        help='Target Language')
    parser.add_argument('-i','--input', required=True,
                        help='Input file')
    parser.add_argument('-o', '--output', required=True,
                        help='Output file')

    parser.add_argument('--tool-script-dir', default=os.path.join(BASE_DIR, 'wyz_mttool_scripts'),
                        help='Path to the tool script dir')

    opt = parser.parse_args()

    post_edit(opt)

if __name__ == '__main__':
    main()