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
import logging
import ndjson

from uuid import uuid4

parser = argparse.ArgumentParser(description='Data Ingestion Tool')
parser.add_argument("--input_json", required=True, default=None, type=str)
parser.add_argument("--output_json", required=True, default=None, type=str)

args = parser.parse_args()
logging.getLogger().setLevel(logging.INFO)

utterance_table_keys = [
    "id",
    "text_verbatim",
    "text_original",
    "audio_filepath",
    "duration",
    "gender",
    "age",
    "dist_from_mic",
    "environment",
    "mic_used",
    "accent",
    "scripted",
    "sampling_rate",
    "number_speaker",
    "data_type",
    "speaker_id",
    "domain",
    "original_sampling_rate"
]

def main():

    with open(args.input_json) as f:
        input_json_data = ndjson.load(f)

    for entry in input_json_data:
        entry["id"] = str(uuid4())
        if "text" in entry:
            entry["text_original"] = entry["text"]
            del entry["text"]

        if "number_speaker" in entry and isinstance(entry["number_speaker"], str):
            try:
                entry["number_speaker"] = int(entry["number_speaker"]) if len(entry["number_speaker"]) > 0 else 0
            except ValueError:
                entry["number_speaker"] = 0

        if "sampling_rate" in entry and isinstance(entry["sampling_rate"], str):
            try:
                entry["sampling_rate"] = float(entry["sampling_rate"]) if len(entry["sampling_rate"]) > 0 else 16000.0
            except ValueError:
                entry["sampling_rate"] = 16000.0

        if "original_sampling_rate" in entry and isinstance(entry["original_sampling_rate"], str):
            try:
                entry["original_sampling_rate"] = float(entry["original_sampling_rate"]) if len(entry["original_sampling_rate"]) > 0 else 16000.0
            except ValueError:
                entry["original_sampling_rate"] = 16000.0

        for key in utterance_table_keys:
            if key not in entry:
                if key == "text_original":
                    entry[key] = entry["text_verbatim"]
                elif key == "sampling_rate":
                    entry[key] = 16000
                elif key == "original_sampling_rate":
                    entry[key] = float(entry["sampling_rate"])
                elif key == "number_speaker":
                    entry[key] = 1
                else:
                    entry[key] = ""
        for key in list(entry.keys()):
            if key not in utterance_table_keys:
                del entry[key]

    with open(args.output_json, 'w') as f:
        ndjson.dump(input_json_data, f)
    logging.info('Missing fields fixed!')

if __name__ == "__main__":
    main()
