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

# Copyright (c) 2020, SeanNaren.  All rights reserved.
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

# To convert mp3 files to wav using sox, you must have installed sox with mp3 support
# For example sudo apt-get install libsox-fmt-mp3
import argparse
import csv
import json
import logging
import multiprocessing
import os
import subprocess
import sys
import tarfile
from multiprocessing.pool import ThreadPool
from pathlib import Path
from typing import List

import sox
from sox import Transformer
from tqdm import tqdm

parser = argparse.ArgumentParser(description='Downloads and processes Mozilla Common Voice dataset.')
parser.add_argument("--data_root", default='./data/raw/mcv/', type=str, help="Directory to store the dataset.")
parser.add_argument("--data_temp", default=None, type=str, required=True, help="Directory to store intermediate the dataset.")
parser.add_argument("--data_out", default=None, type=str, required=True, help="Directory to store the final dataset.")
parser.add_argument('--manifest_dir', default='./', type=str, help='Output directory for manifests')
parser.add_argument("--save_meta", default=True, type=bool, help='Flag to save metadata in manifests')
parser.add_argument("--save_relative_path", default=False, type=bool, help='Flag to save relative path in manifests')
parser.add_argument("--num_workers", default=multiprocessing.cpu_count(), type=int, help="Workers to process dataset.")
parser.add_argument('--sample_rate', default=16000, type=int, help='Sample rate')
parser.add_argument('--n_channels', default=1, type=int, help='Number of channels for output wav files')
parser.add_argument(
    '--files_to_process',
    nargs='+',
    default=['test.tsv', 'dev.tsv', 'train.tsv'],
    type=str,
    help='list of *.csv file names to process',
)
parser.add_argument(
    '--version',
    default='cv-corpus-5.1-2020-06-22',
    type=str,
    help='Version of the dataset (obtainable via https://commonvoice.mozilla.org/en/datasets',
)
parser.add_argument(
    '--language',
    default='de',
    type=str,
    help='Which language to download.(default english,'
    'check https://commonvoice.mozilla.org/en/datasets for more language codes',
)
args = parser.parse_args()
logging.getLogger().setLevel(logging.INFO)
logging.getLogger('sox').setLevel(logging.WARN)

def create_manifest(data: List[tuple], output_name: str, manifest_path: str, data_type: str, save_meta: bool, save_relative_path: bool):
    output_file = Path(manifest_path) / output_name
    output_file.parent.mkdir(exist_ok=True, parents=True)

    with output_file.open(mode='w') as f:
        for row in tqdm(data, total=len(data)):            
            if save_meta:
                f.write(
                    json.dumps({'audio_filepath': row['relative_path'] if save_relative_path else row['path'],
                                "duration": row['duration'],
                                "sampling_rate": row['sample_rate'],
                                'original_sampling_rate': row['original_sampling_rate'],
                                'text_verbatim': row['sentence'],
                                'text_original': row['text_original'],
                                "age": row['age'],
                                "gender": row['gender'],
                                "accent": row['accent'],
                                "data_type": data_type}) + '\n'
                )
            else:
                f.write(
                    json.dumps({'audio_filepath': row['path'],
                                "duration": row['duration'],
                                'text': row['text_original'].lower()}) + '\n'
                )


def process_files(csv_file, data_out, data_temp, num_workers):
    """ Read *.csv file description, convert mp3 to wav, process text.
        Save results to data_out.

    Args:
        csv_file: str, path to *.csv file with data description, usually start from 'cv-'
        data_out: str, path to dir to save results; wav/ dir will be created
    """
    wav_dir = os.path.join(data_out, 'wav/')
    os.makedirs(wav_dir, exist_ok=True)
    audio_clips_path = os.path.dirname(csv_file) + '/clips/'
    file_meta_path = os.path.join(data_temp, 'file_meta.txt')

    logging.info('Converting mp3 to wav using {} workers for {}.'.format(num_workers, csv_file))
    try:
        # Get list of files to convert and prepare sox command
        file_list = os.path.join(data_out, 'list.txt')
        subprocess.check_call(f"cat {csv_file} | tail -n +2 | cut -f 2 > {file_list}", shell=True)
        sox_command = f"'echo file:{{}}; sox --no-dither -V3 {audio_clips_path}/{{}} " + wav_dir + "/{/.}.wav" + f" rate {args.sample_rate} channels {args.n_channels}'"
        # Do the conversion using parallel
        #pdb.set_trace()
        subprocess.check_call(f"cat {file_list} | parallel -j {num_workers} --bar {sox_command} 2>&1 | grep -A 4 'Input' | grep -e 'Input File' -e 'Sample Rate' -e Duration > {file_meta_path}", shell=True)

    except subprocess.CalledProcessError as err:
        logging.error("Error {} returned by command {}. Output: {}".format(err.returncode, err.cmd, err.output))
        return

    def parse_file_as_dict(duration_file):
        with open(duration_file) as f:
            file_dict = {}
            while True:
                line1 = f.readline()
                line2 = f.readline()
                line3 = f.readline()
                if not line2:
                    break
                filename = os.path.basename(line1.split(':')[1].strip()).replace("'", "")
                rate = float(line2.split(':')[1].strip())
                duration = int(" ".join(line3.split()).split(' ')[4]) / rate
                file_dict[filename] = { "duration": duration, "original_rate": rate }
        return file_dict


    file_meta = parse_file_as_dict(file_meta_path)
    logging.info('Reading metadata using {} workers for {}'.format(num_workers, csv_file))

    def process(row):
        file_path = row['path']
        base_name = os.path.basename(file_path)
        file_name = os.path.splitext(base_name)[0]
        output_wav_path = os.path.join(wav_dir, file_name + '.wav')

        row['duration'] = float(file_meta[base_name]["duration"])
        row['sample_rate'] = args.sample_rate
        row['original_sampling_rate'] = float(file_meta[base_name]["original_rate"])
        row['path'] = output_wav_path
        row['gender'] = row['gender']
        row['age'] = row['age']
        row['accent'] = row['accent']
        row['text_original'] = row['sentence'].lower().strip()
        return row

    with open(csv_file) as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        next(reader, None)  # skip the headers
        data = [row for row in reader]
        with ThreadPool(num_workers) as pool:
            data = list(tqdm(pool.imap(process, data), total=len(data)))
    return data


def main():
    data_root = args.data_root
    data_out = data_root
    data_temp = data_root
    os.makedirs(data_root, exist_ok=True)

    if args.data_out != None and os.path.exists(args.data_out) == False:
        logging.error('Invalid out dir {}'.format(args.data_out))
        exit(1)
    else:
        data_out = args.data_out

    if args.data_temp != None and os.path.exists(args.data_temp) == False:
        logging.error('Invalid temp dir {}'.format(args.data_temp))
        exit(1)
    else:
        data_temp = args.data_temp

    target_unpacked_dir = os.path.join(data_temp, "CV_unpacked")

    if os.path.exists(target_unpacked_dir):
        logging.info('Find existing folder {}'.format(target_unpacked_dir))
    else:
        filename = f"{args.language}.tar.gz"
        target_file = os.path.join(data_root, os.path.basename(filename))
        if not os.path.exists(target_file):
            logging.info("Could not find Common Voice. Please download German corpus at https://commonvoice.mozilla.org/en/datasets.")
        else:
            logging.info("Found Common Voice Corpus file at {}".format(target_file))

        os.makedirs(target_unpacked_dir, exist_ok=True)
        logging.info("Unpacking corpus to {} ...".format(target_unpacked_dir))
        tar = tarfile.open(target_file)
        tar.extractall(target_unpacked_dir)
        tar.close()

    folder_path = os.path.join(target_unpacked_dir, args.version + f'/{args.language}/')
    logging.info(subprocess.check_output("find {} -maxdepth 3".format(target_unpacked_dir), shell=True))

    for csv_file in args.files_to_process:
        data = process_files(
            csv_file=os.path.join(folder_path, csv_file),
            data_out=os.path.join(data_out, os.path.splitext(csv_file)[0]),
            data_temp=data_temp,
            num_workers=args.num_workers,
        )
        logging.info('Creating manifests...')
        create_manifest(
            data=data,
            output_name=f'mcv_{os.path.splitext(csv_file)[0]}_manifest.json',
            manifest_path=args.manifest_dir,
            data_type=os.path.splitext(csv_file)[0],
            save_meta=args.save_meta,
	        save_relative_path=args.save_relative_path
        )


if __name__ == "__main__":
    main()
