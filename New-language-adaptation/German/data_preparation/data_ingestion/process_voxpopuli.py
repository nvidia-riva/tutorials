import argparse
import json
import subprocess
import os
import sys
import re
import multiprocessing as mp
import tqdm
import logging
import codecs

logging.getLogger().setLevel(logging.INFO)
logging.getLogger('sox').setLevel(logging.WARN)

def parse_arguments():
    parser = argparse.ArgumentParser('Process voxpopuli dataset')
    parser.add_argument('--data_root', help='Root of dataset', required=True, type=str)
    parser.add_argument('--out_dir', help='Output directory', required=True, type=str)
    parser.add_argument('--sample_rate', help='Output audio sample rate', default=16000, type=int)
    parser.add_argument('--num_workers', help='Number of multiworkers', default=os.cpu_count(), type=int)
    parser.add_argument('--lang', help='2 char language-code of dataset, default to German', required=False, default='de')
    parser.add_argument('--sample_size', help="Audio sample size in bits", required=False, default=16)
    parser.add_argument('--num_channel', help="Number of channels", required=False, default=1)
    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(1)
    if len(args.lang) > 2:
        print(f"Please provide 2 char language code")
        sys.exit(1)
    return args

def create_utt(entry):
    idx = entry[0]
    line = entry[1]
    args = entry[2]
    try:
        meta_file = os.path.join(args.out_dir,f'meta_{idx}.txt')
        meta = line.split('\t')
        year = meta[0][:4]
        ogg_file = os.path.join(args.data_root, args.lang, year, meta[0]) + '.ogg'
        wav_file = os.path.join(args.out_dir, meta[4], meta[0]) + '.wav'
        subprocess.check_output(f"sox --no-dither -V3  {ogg_file} -b {args.sample_size} -r {args.sample_rate} -c {args.num_channel} {wav_file}  2>&1 | grep -A 4 'Input' | grep -e 'Sample Rate' -e Duration > {meta_file}", shell=True)
        meta_f = open(meta_file,'r')
        sr_line = meta_f.readline()
        dur_line = meta_f.readline()
        original_sr = float(sr_line.split(':')[1].strip())
        dur = int(" ".join(dur_line.split()).split(' ')[4]) / original_sr

        # remove spurious leading serial number present in some transcripts
        text_original = re.sub(r'^\s*\d+\.', '', meta[1].strip())

        utt = {
            "audio_filepath": wav_file,
            "duration": dur,
            "gender": meta[5].strip(),
            "scripted": "",
            "original_sampling_rate": original_sr,
            "sampling_rate": args.sample_rate,
            "num_speakers": 1,
            "speaker_id": meta[3].strip(),
            "text_verbatim": meta[1].strip(),
            "text_original": text_original,
            "data_type": meta[4].strip(),
            "domain": ""
            }
        if os.path.exists(meta_file):
            os.remove(meta_file)
    except Exception as e:
        logging.error(f"Error {e} returned.")
        exit()
    return utt


def process(args):
    types = ['train', 'test', 'dev']
    base_dir = os.path.join(args.data_root,args.lang)

    pool = mp.Pool(processes=args.num_workers)
    manifest_entries = []
    for t in types:
        subprocess.check_output(f"mkdir -p {args.out_dir}/{t}", shell=True)
        fin = open(os.path.join(base_dir,f"asr_{t}.tsv"),'r',encoding="utf-8")
        lines = [(idx,line,args) for idx,line in enumerate(fin) if line.split()!='' and idx!=0]
        result = list(tqdm.tqdm(pool.imap(create_utt, lines),total=len(lines)))
        #manifest_entries.extend(result)
        manifest_entries = result
    
        with codecs.open(os.path.join(args.out_dir,f"voxpopuli_{t}_manifest.json"), 'w', encoding='utf-8') as fout:
            for m in manifest_entries:
                fout.write(json.dumps(m, ensure_ascii=False) + '\n')
        fout.close()

    

if __name__ == '__main__':
    args = parse_arguments()
    process(args)
