#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
基于
'''

import argparse
import itertools
import os
from gensim import utils
from gensim.models.word2vec import Word2Vec, LineSentence, MAX_WORDS_IN_BATCH

class BELineSentence(LineSentence):

    def __init__(self, source, max_sentence_length=MAX_WORDS_IN_BATCH, limit=None, sos_token='<SOS>', eos_token='<EOS>'):
        super(BELineSentence, self).__init__(source, max_sentence_length, limit)
        self.sos_token = sos_token
        self.eos_token = eos_token

    def __iter__(self):
        """Iterate through the lines in the source."""
        try:
            # Assume it is a file-like object and try treating it as such
            # Things that don't have seek will trigger an exception
            self.source.seek(0)
            for line in itertools.islice(self.source, self.limit):
                line = utils.to_unicode(line).split()
                i = 0
                while i < len(line):
                    yield line[i: i + self.max_sentence_length]
                    i += self.max_sentence_length
        except AttributeError:
            # If it didn't work like a file, use it as a string filename
            with utils.smart_open(self.source) as fin:
                for line in itertools.islice(fin, self.limit):
                    line = utils.to_unicode(line).split()
                    i = 0
                    while i < len(line):
                        yield [self.sos_token] + line[i: i + self.max_sentence_length - 2] + [self.eos_token]
                        i += self.max_sentence_length

def main():
    parser = argparse.ArgumentParser(description='Generate vectors for word embedding from existed corpus.')

    parser.add_argument('-i', '--input', type=str, required=True,
                        help='path to the corpus file')

    parser.add_argument('-o', '--output', type=str, required=True,
                        help='path to save the output file')

    parser.add_argument('-e', '--encoding', type=str, default='utf-8',
                        help='codec for non-ascii file\ndefault: utf-8')

    parser.add_argument('-f', '--format', type=str, default='bin',
                        help='output format. "bin" for binary output and "text" for textual output.\ndefault: bin')

    parser.add_argument('-d', '--dimension', type=int, default=512,
                        help='word2vec size.\ndefault: 512')

    parser.add_argument('-w', '--window', type=int, default=8,
                        help='window size for cbow or skip-gram.\ndefault: 8')

    parser.add_argument('-m', '--min_count', type=int, default=5,
                        help='minimum count to filter words.\ndefault: 5')

    parser.add_argument('--sos_token', type=str, default='<s>',
                        help='Token that represents the start of a sentence.')

    parser.add_argument('--eos_token', type=str, default='</s>',
                        help='Token that represents the end of a sentence.')

    parser.add_argument('--model_struc', type=str, default='cbow',
                        help='model structure. Options are "cbow" or "skip-gram".\ndefault: cbow')

    parser.add_argument('--output_optim', type=str, default='ns',
                        help='output layer optimization. Options are "ns" or "hs"\ndefault: ns')

    parser.add_argument('--workers', type=int, default=10,
                        help='workers to train word2vec.\ndefualt: 10')

    parser.add_argument('--vocab', action='store_true',
                        help='whether output the vocabulary file meanwhile.\n')

    opt = parser.parse_args()

    if not os.path.isfile(opt.src):
        raise Exception('File not Found')

    sentences = BELineSentence(opt.src, sos_token=opt.sos_token, eos_token=opt.eos_token)

    sg = 0 if opt.model_struc.strip() == 'cbow' else 1
    hs = 0 if opt.output_optim.strip() == 'ns' else 1
    model = Word2Vec(sentences, size=opt.size, window=opt.window, min_count=opt.min_count, workers=opt.workers, sg=sg, hs=hs)

    if opt.output == 'bin':
        model.save(opt.trg)
    elif opt.output == 'text':
        model.wv.save_word2vec_format(opt.trg, binary=False)

    if opt.vocab:
        trg_prefix = os.path.dirname(os.path.abspath(opt.trg))
        with open(os.path.join(trg_prefix, 'vocab'), 'w') as vocab_f:
            for w in model.wv.vocab:
                vocab_f.write('{}\n'.format(w.encode(opt.encoding)))


if __name__ == '__main__':
    main()
'''
python make_word2vec.py -s data/en/bpe.tokens -t /data/en/word2vec -o text --vocab
'''
