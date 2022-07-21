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
#
# USAGE: python get_librispeech_data.py --data_root=<where to put data>
#        --data_set=<datasets_to_download> --num_workers=<number of parallel workers>
# where <datasets_to_download> can be: dev_clean, dev_other, test_clean,
# test_other, train_clean_100, train_clean_360, train_other_500 or ALL
# You can also put more than one data_set comma-separated:
# --data_set=dev_clean,train_clean_100
import argparse
import fnmatch
import functools
import json
import logging
import multiprocessing
import os
import subprocess
import tarfile
import urllib.request

from sox import Transformer
from tqdm import tqdm

parser = argparse.ArgumentParser(description='LibriSpeech Data download')
parser.add_argument("--data_root", default=None, type=str)
parser.add_argument("--data_out_dir", default=None, type=str)
parser.add_argument("--json_out", default=None, type=str)
parser.add_argument("--data_sets", default="dev_clean", type=str)
parser.add_argument("--extracted_dir", default=None, type=str)
parser.add_argument("--rate", default=16000, type=int)
parser.add_argument("--num_workers", default=4, type=int)
args = parser.parse_args()
logging.getLogger().setLevel(logging.INFO)
logging.getLogger('sox').setLevel(logging.WARN)

URLS = {
    'train_clean_100': ("http://www.openslr.org/resources/12/train-clean-100.tar.gz"),
    'train_clean_360': ("http://www.openslr.org/resources/12/train-clean-360.tar.gz"),
    'train_other_500': ("http://www.openslr.org/resources/12/train-other-500.tar.gz"),
    'dev_clean': "http://www.openslr.org/resources/12/dev-clean.tar.gz",
    'dev_other': "http://www.openslr.org/resources/12/dev-other.tar.gz",
    'test_clean': "http://www.openslr.org/resources/12/test-clean.tar.gz",
    'test_other': "http://www.openslr.org/resources/12/test-other.tar.gz",
}


def __maybe_download_file(destination: str, source: str):
    """
    Downloads source to destination if it doesn't exist.
    If exists, skips download
    Args:
        destination: local filepath
        source: url of resource
    Returns:
    """
    source = URLS[source]
    if not os.path.exists(destination):
        logging.info("{0} does not exist. Downloading ...".format(destination))
        urllib.request.urlretrieve(source, filename=destination + '.tmp')
        os.rename(destination + '.tmp', destination)
        logging.info("Downloaded {0}.".format(destination))
    else:
        logging.info("Destination {0} exists. Skipping.".format(destination))
    return destination


def __extract_file(filepath: str, data_dir: str):
    logging.info("Extracting to {0}".format(data_dir))
    try:
        tar = tarfile.open(filepath)
        tar.extractall(data_dir)
        tar.close()
    except Exception:
        logging.info('Not extracting. Maybe already there?')

def __read_speaker_info(data_folder: str):
    speaker_info = {}
    with open(os.path.join(os.path.dirname(data_folder), "SPEAKERS.TXT"), encoding="utf-8") as fin:
        for line in fin:
            if line[0] != ';':
                fields = line.strip().replace(' ', '').split(sep='|')
                info = { 'gender': "male" if fields[1] == 'M' else "female" if fields[1] == 'F' else ""  }
                speaker_info[fields[0]] = info
    return speaker_info

def __process_transcript(file_path: str, dst_folder: str, speaker_info: dict):
    """
    Converts flac files to wav from a given transcript, capturing the metadata.
    Args:
        file_path: path to a source transcript  with flac sources
        dst_folder: path where wav files will be stored
    Returns:
        a list of metadata entries for processed files.
    """
    entries = []
    root = os.path.dirname(file_path)
    with open(file_path, encoding="utf-8") as fin:
        for line in fin:
            id, text = line[: line.index(" ")], line[line.index(" ") + 1 :]
            transcript_text = text.lower().strip()

            # Convert FLAC file to WAV
            flac_file = os.path.join(root, id + ".flac")
            wav_file = os.path.join(dst_folder, id + ".wav")
            if not os.path.exists(wav_file):
                tfm = Transformer()
                tfm.set_globals(dither=False)
                tfm.set_output_format(rate=args.rate)
                tfm.build(flac_file, wav_file)

            # check duration
            duration = subprocess.check_output("soxi -D {0}".format(wav_file), shell=True)

            entry = {}
            entry['audio_filepath'] = os.path.abspath(wav_file)
            entry['duration'] = float(duration)
            entry['text'] = transcript_text
            entry['gender'] = speaker_info[id.split(sep='-')[0]]['gender']
            entry['speaker_id'] = id.split(sep='-')[0]
            entry['sampling_rate'] = args.rate
            entry['original_sampling_rate'] = 16000
            entries.append(entry)
    return entries


def __process_data(data_folder: str, dst_folder: str, manifest_file: str, num_workers: int):
    """
    Converts flac to wav and build manifests's json
    Args:
        data_folder: source with flac files
        dst_folder: where wav files will be stored
        manifest_file: where to store manifest
        num_workers: number of parallel workers processing files
    Returns:
    """

    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)

    files = []
    entries = []

    speaker_info = __read_speaker_info(data_folder)

    for root, dirnames, filenames in os.walk(data_folder):
        for filename in fnmatch.filter(filenames, '*.trans.txt'):
            files.append(os.path.join(root, filename))

    with multiprocessing.Pool(num_workers) as p:
        processing_func = functools.partial(__process_transcript, dst_folder=dst_folder, speaker_info=speaker_info)
        results = p.imap(processing_func, files)
        for result in tqdm(results, total=len(files)):
            entries.extend(result)

    with open(manifest_file, 'w') as fout:
        for m in entries:
            fout.write(json.dumps(m) + '\n')


def main():
    if args.extracted_dir == None and args.data_root == None:
        parser.print_help()
        exit()

    data_root = args.data_root
    data_sets = args.data_sets
    num_workers = args.num_workers

    if data_sets == "ALL":
        data_sets = "dev_clean,dev_other,train_clean_100,train_clean_360,train_other_500,test_clean,test_other"

    if args.extracted_dir != None:
        if args.data_out_dir == None:
            logging.info("Must specify data_out_dir when using extracted_dir")
            parser.print_help()
            exit()

        logging.info("Processing files at {0}".format(args.extracted_dir))
        __process_data(
            os.path.join(args.extracted_dir, "LibriSpeech"),
            os.path.join(args.data_out_dir, "LibriSpeech"),
            os.path.join(args.data_out_dir, args.json_out),
            num_workers=num_workers,
        )
        exit()

    for data_set in data_sets.split(','):
        logging.info("\n\nWorking on: {0}".format(data_set))
        filepath = os.path.join(data_root, data_set + ".tar.gz")
        logging.info("Getting {0}".format(data_set))
        __maybe_download_file(filepath, data_set)
        logging.info("Extracting {0}".format(data_set))
        __extract_file(filepath, data_root)
        logging.info("Processing {0}".format(data_set))
        __process_data(
            os.path.join(os.path.join(data_root, "LibriSpeech"), data_set.replace("_", "-"),),
            os.path.join(os.path.join(data_root, "LibriSpeech"), data_set.replace("_", "-"),) + "-processed",
            os.path.join(os.path.join(data_root, "LibriSpeech"), data_set + "_manifest.json"),
            num_workers=num_workers,
        )
    logging.info('Done!')


if __name__ == "__main__":
    main()
