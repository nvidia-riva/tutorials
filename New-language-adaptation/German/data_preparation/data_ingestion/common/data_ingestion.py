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

import argparse
import fnmatch
import json
import logging
import os
import sys
import subprocess
import maglev
import pandas as pd
from uuid import uuid4
import datetime
import yaml
import multiprocessing

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../'))
import datasets

parser = argparse.ArgumentParser(description='Data Ingestion Tool')
parser.add_argument("--config", required=True, default=None, type=str)
parser.add_argument("--data_root", required=True, default=None, type=str)
parser.add_argument("--data_output", required=True, default=None, type=str)
parser.add_argument("--temp_dir", required=True, default=None, type=str)
parser.add_argument("--database", required=False, default=None, type=str)
parser.add_argument("--data_table", required=False, default=None, type=str)
parser.add_argument("--utterance_table", required=False, default=None, type=str)
parser.add_argument("--ingestion_table", required=False, default=None, type=str)
parser.add_argument("--swift_container", required=False, default=None, type=str)
parser.add_argument("--swift_subdir", required=False, default=None, type=str)
parser.add_argument("--reset_tables", required=True, choices=["true", "false"], type=str)
parser.add_argument('--num_workers', required=False, default=multiprocessing.cpu_count(), type=int)
parser.add_argument("--skip", required=False, default=None, type=str, help='comma separated list of datasets to skip')
parser.add_argument("--only", required=False, default=None, type=str, help='comma separated list of datasets to process')
parser.add_argument('--upload', dest='upload', action='store_true')
parser.add_argument('--split_mode', dest='split_mode', action='store_true')

args = parser.parse_args()
logging.getLogger().setLevel(logging.INFO)

try:
    config = yaml.safe_load(open(args.config))
except:
    logging.error("Invalid config file: {}".format(args.config))
    exit(1)

# Load from config
database_name = config["catalog_tables"]["db_database_name"]
datasets_table_name = config["catalog_tables"]["db_dataset_name"]
utterances_table_name = config["catalog_tables"]["db_utterance_items_name"]
swift_container = config["swift_container"]
swift_container_directory = config["swift_container_directory"]

# TODO add code to override names via command line


num_workers = "--num_workers {}".format(args.num_workers) if args.num_workers is not None else  ""
extracted_datasets_dir = os.path.join(args.temp_dir, "datasets")
os.makedirs(extracted_datasets_dir, exist_ok=True)
maglev_client = maglev.Client.default_service_client()

def __check_dataset_exists(dataset_info: dict):
    """
    Returns: True if dataset exists in database, otherwise False
    """
    dataset = pd.DataFrame()
    try:
        dataset = maglev_client.get_table(datasets_table_name, database_name, partitions=[f"id={dataset_info['id']}"]).to_pandas()
    except ValueError:
        logging.debug(f"No partition found for dataset {dataset_info['id']}")
    except Exception as err:
        logging.error(f"Exception occured: {err}")
        exit(1)
    if dataset.empty:
        return False
    else:
        return True


def check_dataset_ingested(database_name, utterances_table_name, dataset_info, ingestion_version):
    last_ingestion = pd.DataFrame()
    if maglev_client.table_exists_udc(utterances_table_name, database_name):
        query = "select dataset_id, ingestion_version from {}.{} where dataset_id='{}' and ingestion_version='{}' limit 1".format(database_name, utterances_table_name, dataset_info["id"], ingestion_version)
        logging.info("Running query to check if dataset is already ingested. Query: {}".format(query))
        last_ingestion = maglev_client.run_query(query).to_pandas()
    return last_ingestion


def main():
    script_base_dir = os.path.dirname(os.path.realpath(__file__))
    data_roots = args.data_root.split(",")
    args.data_output = args.data_output.rstrip("/")
    data_output_base_dir = os.path.join(args.data_output, swift_container_directory)
    temp_dir = args.temp_dir
    reset_tables = True if args.reset_tables == "true" else False

    # Create output directory
    os.makedirs(data_output_base_dir, exist_ok=True)

    # Deleting datasets and utterances table if the reset flag is set to true
    if reset_tables == True:
        logging.info("Resetting tables")
        if maglev_client.table_exists_udc(datasets_table_name, database_name):
            maglev_client.delete_table(datasets_table_name, database_name)
        if maglev_client.table_exists_udc(utterances_table_name, database_name):
            maglev_client.delete_table(utterances_table_name, database_name)


    dataset_info_list = []
    for data_root in data_roots:
        for root, dirnames, filenames in os.walk(data_root):
            for filename in fnmatch.filter(filenames, 'dataset_info.json'):
                logging.info("Found dataset at {0}".format(os.path.join(root, filename)))
                dataset_info_list.append(os.path.join(root, filename))

    # Read from config
    if 'ingestion' in config:
        ingestion_params = config['ingestion']
        ingestion_params['seed'] = config['seed']
        if 'rate' not in ingestion_params:
            ingestion_params['rate'] = 16000
        if not ('num_workers' in ingestion_params and ingestion_params['num_workers'] > 0):
            ingestion_params['num_workers'] = args.num_workers
    else:
        ingestion_params = {'rate': 16000, 'num_workers': args.num_workers}
    num_datasets_processed = 0
    num_datasets_already_exists = 0
    num_datasets_failed = 0
    num_datasets_skipped = 0
    ingestion_durations = {}
    selected_datasets_file = "{}.txt".format(os.path.join(args.temp_dir, "selected_datasets"))

    for dataset_info_file in dataset_info_list:
        logging.info("Processing dataset at {0}".format(dataset_info_file))
        with open(dataset_info_file) as f:
            dataset_info = json.load(f)

            if dataset_info["status"].lower() != "active":
                logging.info(f"Dataset {dataset_info['name']} {dataset_info['version']} not active. Skipping.")
                num_datasets_skipped += 1
                continue

            if config["language"].lower() not in dataset_info["language"].lower():
                logging.error(f"Language mismatch for dataset {dataset_info['name']} {dataset_info['version']}")
                logging.error(f"Language in config: {config['language']} Language in dataset: {dataset_info['language']}")
                num_datasets_skipped += 1
                continue

            name_and_version = dataset_info["name"]
            if len(dataset_info["version"]):
                name_and_version = name_and_version + "_" + dataset_info["version"]

            if args.skip is not None:
                skipped_datasets = args.skip.split(",")
                if name_and_version in skipped_datasets:
                    logging.info("{} is skipped".format(name_and_version))
                    num_datasets_skipped += 1
                    continue

            if args.only is not None:
                only_datasets = args.only.split(",")
                if name_and_version not in only_datasets:
                    logging.info("{} is not selected".format(name_and_version))
                    num_datasets_skipped += 1
                    continue

            dataset = datasets.get_dataset_handler(dataset_info_file)
            if (dataset == None):
                logging.error("No handler found {} for dataset at {}".format(dataset, dataset_info_file))
                num_datasets_skipped += 1
                continue

            # Check if this dataset and version was already ingested with latest ingestion version
            ingestion_version = dataset.get_version()
            if ingestion_version == None:
                logging.error("Invalid ingestion_version: {}".format(ingestion_version))
                num_datasets_failed += 1
                continue

            last_ingestion = check_dataset_ingested(database_name, utterances_table_name, dataset_info, ingestion_version)

            if last_ingestion.empty:
                logging.info("No ingestion found for dataset {} version {} ingestion_version {}".format(dataset_info["name"], dataset_info["version"], ingestion_version))
            else:
                logging.info("Ingestion found for dataset {} version {} ingestion_version {}".format(dataset_info["name"], dataset_info["version"], ingestion_version))
                logging.info("Skipping...")
                num_datasets_already_exists += 1
                continue

            logging.info("Found handler {} for dataset at {}".format(dataset, dataset_info_file))

            if args.split_mode is True:
                with open(selected_datasets_file, 'a', encoding='utf-8') as f:
                    f.write(dataset_info_file.replace(args.data_root, "").replace("dataset_info.json", "") + '\n')
                continue

            dataset_out_dir = os.path.join(data_output_base_dir, name_and_version)
            os.makedirs(dataset_out_dir, exist_ok=True)

            # Dataset processing
            start_time = datetime.datetime.now()
            manifest_file, ret = dataset.process(dataset_info_file, temp_dir, dataset_out_dir, ingestion_params)
            if ret != 0 or os.path.isfile(manifest_file) == False:
                logging.error("Importing dataset failed.")
                # Clear output directory
                subprocess.check_output("rm -rf {}/*".format(data_output_base_dir), shell=True)
                subprocess.check_output("rm -rf {}/*".format(temp_dir), shell=True)
                num_datasets_failed += 1
                continue

            updated_datasets_table = False

            try:
                # Upload audio data
                if args.upload is True:
                    # Upload output contents to Swift
                    file_stdout = open(os.path.join(temp_dir, "swift_stdout.txt"), "w")
                    file_stderr = open(os.path.join(temp_dir, "swift_stderr.txt"), "w")
                    logging.info("Uploading {} dataset to {} container".format(dataset_info["name"], swift_container))
                    logging.info("Saving stdout and stderr to files in {}".format(temp_dir))
                    subprocess.check_call("cd {}; swift upload --object-threads {} {} .".format(args.data_output, args.num_workers, swift_container), shell=True, stdout=file_stdout, stderr=file_stderr)

                # Update database
                # Fix missing fields
                manifest_file_fixed = os.path.splitext(manifest_file)[0] + "_fixed.json"
                subprocess.check_output("python {}/fix_missing_fields.py --input_json {} --output_json {}".format(script_base_dir, manifest_file, manifest_file_fixed), shell=True)
                subprocess.check_output("mv {} {} ".format(manifest_file_fixed, manifest_file), shell=True)

                # Remove absolute path
                logging.info("Removing absolute path: {0}".format(data_output_base_dir))
                subprocess.check_output(f"sed -i 's#{args.data_output}/##g' {manifest_file}", shell=True)

                # Update datasets table
                # Check if datasets table already has entry
                created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if maglev_client.table_exists_udc(datasets_table_name, database_name) and __check_dataset_exists(dataset_info) == True:
                    logging.info("Dataset {} already exists. Overwriting entry in {}.{}".format(dataset_info["name"], database_name, datasets_table_name))
                    maglev_client.delete_partition_from_udc(f"id={dataset_info['id']}", datasets_table_name, database_name)

                logging.info("Updating datasets table: {}.{}".format(database_name, datasets_table_name))
                try:
                    dataset_df = pd.read_json(dataset_info_file, dtype={'version': 'str'}, lines=True)
                except:
                    with open(dataset_info_file, 'r') as f:
                        dataset_df = pd.DataFrame([json.load(f)])
                dataset_df = dataset_df.drop(columns=['id'])
                dataset_df['created_at'] = created_at
                dataset_tbl = maglev.udc.CatalogTable.from_pandas(dataset_df, datasets_table_name, database_name, "id={}".format(dataset_info["id"]))
                maglev_client.upload_table(dataset_tbl)
                updated_datasets_table = True

                # Update utterances table
                # Check if utterances table has entries populated by any simultaneous jobs
                if check_dataset_ingested(database_name, utterances_table_name, dataset_info, ingestion_version).empty:
                    logging.info("Updating utterances table: {}.{}".format(database_name, utterances_table_name))
                    subprocess.check_output("maglev catalog upload -f {} -d {} -t {} -o jsonl --partition=dataset_id={}/ingestion_version={}/created_at=\"{}\"".format(manifest_file, database_name, utterances_table_name, dataset_info["id"], ingestion_version, created_at), shell=True)
                else:
                    logging.info("Dataset {} {} got ingested by a simultaneous job. Not adding entries in {}.{}".format(dataset_info["name"], dataset_info["version"], database_name, utterances_table_name))

            except (Exception, subprocess.CalledProcessError) as err:
                #logging.error("Error {} returned by command {}. Output: {}".format(err.returncode, err.cmd, err.output))
                logging.error("Exception occured.")
                logging.error(err)
                subprocess.check_output("rm -rf {}/*".format(data_output_base_dir), shell=True)
                subprocess.check_output("rm -rf {}/*".format(temp_dir), shell=True)
                if updated_datasets_table:
                    maglev_client.delete_partition_from_udc(f"id={dataset_info['id']}", datasets_table_name, database_name)

                num_datasets_failed += 1
                continue

            # Clear output directory
            subprocess.check_output("rm -rf {}/*".format(data_output_base_dir), shell=True)
            subprocess.check_output("rm -rf {}/*".format(temp_dir), shell=True)
            num_datasets_processed += 1

            end_time = datetime.datetime.now()
            ingestion_durations[name_and_version] = datetime.timedelta(seconds=(end_time - start_time).total_seconds())

    for dataset in ingestion_durations:
        logging.info("Ingestion time for {}: {}".format(dataset, ingestion_durations[dataset]))

    logging.info("Number of datasets processed: {}".format(num_datasets_processed))
    logging.info("Number of datasets already exists: {}".format(num_datasets_already_exists))
    logging.info("Number of datasets failed: {}".format(num_datasets_failed))
    logging.info("Number of datasets skipped: {}".format(num_datasets_skipped))
    exit(num_datasets_failed)

if __name__ == "__main__":
    main()
