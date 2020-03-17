#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
This script can remove bpe symbol in a corpus file.
It is written for unity with other tool scripts.
Or you can just run command: "sed -r 's/(@@ )|(@@ ?$)//g' <input_file> > <output_file>",
'''

import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input', required=True,
                        help='Path the input file.')
    parser.add_argument('-o', '--output', required=True,
                        help='Path the output file.')
    parser.add_argument('--encoding', default='utf-8',
                        help='Encoding format to open/save the file.')

    opt = parser.parse_args()

    cmd = 'sed -r \'s/(@@ )|(@@ ?$)//g\' {} > {}'.format(opt.input, opt.output)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if err:
        raise Exception(err)

if __name__ == '__main__':
    main()