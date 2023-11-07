# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# USAGE: python process_asr_text_tokenizer.py --manifest=<path to train manifest files, seperated by commas> \
#         --data_root="<output directory>" \
#         --vocab_size=<number of tokens in vocabulary> \
#         --tokenizer=<"spe" or "wpe"> \
#         --log
# where <manifest> can be: train_clean_100, train_clean_360, train_other_500
# You can also put more than one data_set comma-separated:
# --manifest="train_clean_100,train_clean_360,train_other_500"
# or
#       python process_asr_text_tokenizer.py --data_file=<path to train text file> \
#         --data_root="<output directory>" \
#         --vocab_size=<number of tokens in vocabulary> \
#         --tokenizer=<"bpe" or "wpe"> \
#         --log
# where <manifest> can be: train_clean_100, train_clean_360, train_other_500
# You can also put more than one data_set comma-separated:
# --manifest="train_clean_100,train_clean_360,train_other_500"
#
# Args:
#   --manifest or --data_file: If your text data lies inside of an ASR manifest file,
#       then use the --manifest path. If instead the text data is inside a file with separate lines
#       corresponding to different text lines, then use --data_file.
#       In either case, you can add commas to concatenate different manifests or different data files.
#
#   --data_root: The output directory (whose subdirectories will be created if not present) where
#       the tokenizers will be placed.
#
#   --vocab_size: The size of the tokenizer vocabulary. Larger vocabularies can accommodate almost entire,
#       words but the decoder size of any model will grow proportionally.
#
#   --tokenizer: Can be either spe or wpe . spe refers to the Google sentencepiece library tokenizer.
#       wpe refers to the HuggingFace BERT Word Piece tokenizer.
#
#   --no_lower_case: When this flag is passed, it will force the tokenizer to create seperate tokens for
#       upper and lower case characters. By default, the script will turn all the text to lower case
#       before tokenization (and if upper case characters are passed during training/inference, the
#       tokenizer will emit a token equivalent to Out-Of-Vocabulary). Used primarily for the
#       English language.
#
#    --spe_type: The sentencepiece library has a few implementations of the tokenization technique, and
#       spe_type refers to these implementations. Currently supported types are unigram, bpe, char, word.
#       Defaults to bpe.
#
#   --spe_character_coverage: The sentencepiece library considers how much of the original vocabulary it
#       should cover in its "base set" of tokens (akin to the lower and upper case characters of the
#       English language). For almost all languages with small base token sets (<1000 tokens), this
#       should be kept at its default of 1.0. For languages with larger vocabularies (say Japanese,
#       Mandarin, Korean etc), the suggested value is 0.9995.
#
#   --spe_sample_size: If the dataset is too large, consider using a sampled dataset indicated by a
#       positive integer. By default, any negative value (default = -1) will use the entire dataset.
#
#   --spe_train_extremely_large_corpus: When training a sentencepiece tokenizer on very large amounts of text,
#       sometimes the tokenizer will run out of memory or wont be able to process so much data on RAM.
#       At some point you might receive the following error - "Input corpus too large, try with
#       train_extremely_large_corpus=true". If your machine has large amounts of RAM, it might still be possible
#       to build the tokenizer using the above flag. Will silently fail if it runs out of RAM.
#
#   --spe_max_sentencepiece_length: Limits the maximum length that any any SentencePiece subword can be.
#       Using this will change the subword tokens generated.
#
#   --spe_pad: Adds <pad> as special token.
#
#   --spe_bos: Adds <s> as Begining-of-Sentence special token.
#
#   --spe_eos: Adds </s> as End-of-Sentence special token.
#
#   --log: Whether the script should display log messages

import argparse
import json
import logging
import os

import tokenizers

from nemo.collections.common.tokenizers.sentencepiece_tokenizer import create_spt_model

parser = argparse.ArgumentParser(description='Create tokenizer')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("--manifest", default=None, type=str, help='Comma separated list of manifest files')
group.add_argument("--data_file", default=None, help='data file from which to create tokenizer model')
parser.add_argument("--data_root", required=True, default=None, type=str, help='Output directory')
parser.add_argument("--vocab_size", default=1024, type=int, help='Vocabulary size')
parser.add_argument("--tokenizer", default="wpe", choices=["spe", "wpe"], help='Type of tokenization to perform')
parser.add_argument(
    "--spe_type",
    default="bpe",
    choices=['bpe', 'unigram', 'char', 'word'],
    help='Type of the SentencePiece model. Can be `bpe`, `unigram`, `char` or `word`.'
    'Used only if --tokenizer == `spe`',
)
parser.add_argument(
    '--spe_character_coverage',
    type=float,
    default=1.0,
    help="Character coverage percentage for SentencePiece tokenization. For languages "
    "with large vocabulary, should be close to 0.9995, otherwise kept as 1.0",
)
parser.add_argument('--spe_bos', action='store_true', help='Add <s> token to SentencePiece Tokenizer.')
parser.add_argument('--spe_eos', action='store_true', help='Add </s> token to SentencePiece Tokenizer.')
parser.add_argument('--spe_pad', action='store_true', help='Add <pad> token to SentencePiece Tokenizer.')
parser.add_argument(
    '--spe_sample_size',
    type=int,
    default=-1,
    help="Samples the dataset by `sample_size` if positive integer, otherwise uses whole dataset",
)
parser.add_argument('--spe_train_extremely_large_corpus', action='store_true', help='')
parser.add_argument(
    '--spe_max_sentencepiece_length',
    type=int,
    default=-1,
    help='Limit the maximum number of tokens in each SentencePiece subword. '
    'Must be a positive integer > 0. By default places no limit on subword length.',
)
parser.add_argument('--no_lower_case', dest='lower_case', action='store_false')
parser.add_argument("--log", action='store_true')
parser.set_defaults(log=False, lower_case=True, spe_train_extremely_large_corpus=False)
args = parser.parse_args()


def __build_document_from_manifests(
    data_root: str, manifests: str,
):
    if ',' in manifests:
        manifests = manifests.split(',')
    else:
        manifests = [manifests]

    document_dir = os.path.join(data_root, 'text_corpus')
    if not os.path.exists(document_dir):
        os.makedirs(document_dir)

    document_path = os.path.join(document_dir, 'document.txt')

    if os.path.exists(document_path):
        logging.info('Corpus already exists at path : %s', document_path)
        return document_path

    num_lines = 0
    with open(document_path, 'w') as out_writer:
        for manifest in manifests:
            with open(manifest, 'r') as in_reader:
                for line in in_reader:
                    item = json.loads(line)
                    text = item['text']

                    out_writer.write(text + '\n')
                    out_writer.flush()

                    num_lines += 1

            logging.info(f"Finished extracting manifest : {manifest}")

        logging.info("Finished extracting all manifests ! Number of sentences : {}".format(num_lines))
    return document_path


def __process_data(
    text_path: str,
    dst_folder: str,
    vocab_size: int,
    tokenizer_type: str,
    spe_type: str,
    spe_character_coverage: float,
    spe_train_extremely_large_corpus: bool,
    spe_sample_size: int,
    spe_max_sentencepiece_length: int,
    spe_bos: bool,
    spe_eos: bool,
    spe_pad: bool,
    lower_case: bool,
):
    """
    Converts flac to wav and build manifests's json
    Args:
        text_path: source with text lines
        dst_folder: where wav files will be stored
        vocab_size: vocabular size used in encoding the text
        tokenizer_type: type of tokenization to perform - wpe or spe
        spe_type: type of tokenization model used for spe.
        spe_character_coverage: float value between 0 and 1 (as a percentage). For languages with a vast charset,
            can be < 1.0, but for all other languages, it should be set as 1.0
        spe_sample_size: int, default of -1. If positive integer is used, samples the dataset
            by given sample size.
        spe_train_extremely_large_corpus: bool. If dataset is too large, and user has sufficient RAM,
            this flag can be set to try to trained the tokenizer. Will silently fail if it runs out of RAM.
        spe_max_sentencepiece_length: Limits the maximum length of the SentencePiece subword that can be constructed.
            By default, no limit is placed.
        spe_bos: Bool flag, whether to add <s> to SentencePiece tokenizer vocabulary.
        spe_eos: Bool flag, whether to add </s> to SentencePiece tokenizer vocabulary.
        spe_pad: Bool flag, whether to add <pad> to SentencePiece tokenizer vocabulary.
        lower_case: whether to tokenize with lower case character set only (for english)

    Returns:
    """
    if tokenizer_type == 'spe':

        # Prepare directory of tokenizer
        if spe_max_sentencepiece_length > 0:
            tokenizer_dir = os.path.join(dst_folder, 'tokenizer_{}_{}_v{}_max_{}').format(
                tokenizer_type, spe_type, vocab_size, spe_max_sentencepiece_length
            )
        else:
            tokenizer_dir = os.path.join(dst_folder, 'tokenizer_{}_{}_v{}').format(
                tokenizer_type, spe_type, vocab_size
            )

        if spe_pad:
            tokenizer_dir = f'{tokenizer_dir}_pad'
        if spe_bos:
            tokenizer_dir = f'{tokenizer_dir}_bos'
        if spe_eos:
            tokenizer_dir = f'{tokenizer_dir}_eos'

        if not os.path.exists(tokenizer_dir):
            os.makedirs(tokenizer_dir)

        if os.path.exists(os.path.join(tokenizer_dir, 'tokenizer.model')):
            logging.warning("Model file already exists, overriding old model file !")
            os.remove(os.path.join(tokenizer_dir, 'tokenizer.model'))

        # Build tokenizer
        tokenizer_path, vocab_path = create_spt_model(
            data_file=text_path,
            vocab_size=vocab_size,
            sample_size=spe_sample_size,
            do_lower_case=lower_case,
            output_dir=tokenizer_dir,
            tokenizer_type=spe_type,
            character_coverage=spe_character_coverage,
            train_extremely_large_corpus=spe_train_extremely_large_corpus,
            max_sentencepiece_length=spe_max_sentencepiece_length,
            bos=spe_bos,
            eos=spe_eos,
            pad=spe_pad,
        )

    else:
        tokenizer_dir = os.path.join(dst_folder, 'tokenizer_{}_v{}').format(tokenizer_type, vocab_size)

        if not os.path.exists(tokenizer_dir):
            os.makedirs(tokenizer_dir)

        tokenizer = tokenizers.BertWordPieceTokenizer(lowercase=lower_case)

        tokenizer.train(text_path, vocab_size=vocab_size)
        tokenizer.save_model(tokenizer_dir)

    return tokenizer_dir


def main():
    data_root = args.data_root
    manifests = args.manifest
    data_file = args.data_file
    vocab_size = args.vocab_size
    tokenizer = args.tokenizer
    spe_type = args.spe_type
    spe_character_coverage = args.spe_character_coverage
    spe_sample_size = args.spe_sample_size
    spe_train_extremely_large_corpus = args.spe_train_extremely_large_corpus
    spe_max_sentencepiece_length = args.spe_max_sentencepiece_length
    spe_bos, spe_eos, spe_pad = args.spe_bos, args.spe_eos, args.spe_pad
    lower_case = args.lower_case

    if not os.path.exists(data_root):
        os.makedirs(data_root)

    if args.log:
        logging.basicConfig(level=logging.INFO)

    if manifests:
        text_corpus_path = __build_document_from_manifests(data_root, manifests)
    else:
        text_corpus_path = data_file
    tokenizer_path = __process_data(
        text_corpus_path,
        data_root,
        vocab_size,
        tokenizer,
        spe_type,
        lower_case=lower_case,
        spe_character_coverage=spe_character_coverage,
        spe_sample_size=spe_sample_size,
        spe_train_extremely_large_corpus=spe_train_extremely_large_corpus,
        spe_max_sentencepiece_length=spe_max_sentencepiece_length,
        spe_bos=spe_bos,
        spe_eos=spe_eos,
        spe_pad=spe_pad,
    )

    print("Serialized tokenizer at location :", tokenizer_path)
    logging.info('Done!')


if __name__ == "__main__":
    main()
