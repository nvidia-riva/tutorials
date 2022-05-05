# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import sys
from tqdm import tqdm
import os
import subprocess
import json
import codecs
import unidecode
from multiprocessing import Pool
import argparse
import logging

g_gender = {}
g_data = []

logging.getLogger().setLevel(logging.INFO)
logging.getLogger('sox').setLevel(logging.WARN)

def parse_args():
  parser = argparse.ArgumentParser(
    description='Process MLS dataset')
  parser.add_argument('--dataset_root', type=str,
                        help="Path to dataset's root dir",
                        required=True)
  parser.add_argument('--out_dir', type=str,
                        help="Path to store data manifest and audio.wav files",
                        required=True)
  parser.add_argument('--num_workers', type=int,
                        help="No of multiprocessing workers, Defaults to os.cpu_count()",
                        required=False,
                        default = os.cpu_count())
  parser.add_argument('--sample_size', type=int,
                        help="Audio sample size",
                        required=False,
                        default = 16)
  parser.add_argument('--sample_rate', type=int,
                        required=False,
                        default = 16000,
                        help="Sample rate")
  parser.add_argument('--num_channel',type=int,
                        default=1,
                        required=False,
                        help="Number of output channel")
  return parser.parse_args()

def tsv_to_manifest(args):

  global g_gender, g_data
  meta = open(os.path.join(args.dataset_root, 'metainfo.txt'), 'r', encoding='utf-8')
  raw_meta_data = meta.readlines()
  meta.close()
  for i in raw_meta_data[1:]:
    line = i.strip().replace(" ",'').split("|")
    g_gender[line[0]] = line[1]

  manifests = []
  dirs = ['dev', 'test', 'train']
  manifest_file = args.out_dir + '/manifest.json'

  for dir in dirs:
    manifests = []
    manifest_file = args.out_dir + f'/mls_{dir}_manifest.json'
    
    logging.info('Processing: {0}'.format(dir))
    dt = open(os.path.join(args.dataset_root, dir, 'transcripts.txt'), encoding='utf8')
    g_data = dt.readlines()
    dt.close()

    ## multi-processing
    proc_pool = Pool(args.num_workers)
    per_proc_size = len(g_data) // args.num_workers
    index = []
    for i in range(args.num_workers-1):
      index.append((per_proc_size*i, per_proc_size, args, dir))
    index.append((per_proc_size*(args.num_workers-1), len(g_data) - per_proc_size*(args.num_workers-1), args, dir))
    results_multi = proc_pool.map(proc_tvs_to_manifest, index)

    for i in results_multi:
        if len(i)>0:
          manifests.extend(i)

    with codecs.open(manifest_file, 'w', encoding='utf-8') as fout:
       for m in manifests:
          fout.write(json.dumps(m, ensure_ascii=False) + '\n')
    fout.close()

def proc_tvs_to_manifest(tup):
  start_indx, size, args, data_type = tup
  global g_data
  meta_file = os.path.join(args.out_dir,f'meta_{start_indx}.txt')
  manifests = []
  for i in tqdm(g_data[start_indx:start_indx+size]):
    try:
      i = i.strip().split('\t')
      text = i[1].strip()
      dirs = i[0].strip().split('_')

      os.system("mkdir -p {0}/{1}".format(args.out_dir,data_type))
      flac_file = os.path.join(args.dataset_root, data_type, "audio", dirs[0], dirs[1], i[0]+'.flac')
      wav_file = "{0}/{1}/".format(args.out_dir,data_type) + i[0] + ".wav"
      subprocess.check_output(f"sox --no-dither -V3 -b {args.sample_size} {flac_file} {wav_file} rate {args.sample_rate} channels {args.num_channel}  2>&1 | grep -A 4 'Input' | grep -e 'Sample Rate' -e Duration > {meta_file}", shell=True)
      meta_f = open(meta_file,'r')
      line1 = meta_f.readline()
      line2 = meta_f.readline()
      rate = float(line1.split(':')[1].strip())
      dt = {
        'audio_filepath': os.path.abspath(wav_file),
        'duration': int(" ".join(line2.split()).split(' ')[4]) / rate,
        'sampling_rate': args.sample_rate,
        'gender': g_gender[dirs[0]],
        'speaker_id': dirs[0],
        'text_original': text,
        'original_sampling_rate': rate,
        'number_speaker': 1,
        'data_type': data_type
      }

      manifests.append(dt)
      if os.path.exists(meta_file):
        os.remove(meta_file)
    except Exception as e:
      logging.error(f"Error {e} returned.")
      return {} #return empty manifest
      #exit()
  return manifests

def main():
  args = parse_args()
  tsv_to_manifest(args)

if __name__ == "__main__":
    main()
