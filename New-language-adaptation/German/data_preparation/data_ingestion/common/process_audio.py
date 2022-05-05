import argparse
import json
from tqdm import tqdm
import multiprocessing
from datetime import date
from pathlib import Path
import os

sample_rate = None


def process(dt):
    global sample_rate
    input_wav = dt['audio_filepath']
    output_wav = dt['out_wav']
    cmd = f"sox --no-dither -V1 {input_wav} -r {sample_rate} -c 1 -b 16 {output_wav}"
    try:
        os.system(cmd)
    except Exception as e:
        print(e)
        if input_wav.lower().endswith('.mp3'):
            print(
                'Please install mp3 handler for sox using:\nsudo apt-get install libsox-fmt-mp3')
        exit()
    dt['audio_filepath'] = output_wav
    dt['sample_rate'] = sample_rate
    del dt['out_wav']
    return dt


def check_unique_file_names(data, segments_dir):
    unique_names = set()
    final_data = []
    for info in data:
        dt = json.loads(info)
        audio_path = dt['audio_filepath']
        stem = Path(audio_path).stem
        if stem not in unique_names:
            unique_names.add(stem)
        else:
            stem += str(date.today())
        out_wav = os.path.join(segments_dir, stem + '.wav')
        dt['out_wav'] = out_wav
        final_data.append(dt)
    return final_data


def parse_args():
    parser = argparse.ArgumentParser(
        description='Process audio (convert to 16k 16b mono wavs)')
    parser.add_argument('--input_manifest', type=str,
                        help="Path of input_manifest",
                        required=True)
    parser.add_argument('--segments_dir', type=str,
                        help="Path to store generated segments",
                        required=True)
    parser.add_argument('--output_manifest', type=str,
                        help="Path to store data manifest",
                        required=True)
    parser.add_argument('--num_workers', type=int,
                        help="No of multiprocessing workers, Defaults to os.cpu_count()",
                        required=False)
    parser.add_argument('--sr', type=int, default=16000,
                        help="Sample rate needed for output audio files",
                        required=False)
    return parser.parse_args()


def main():
    global sample_rate
    args = parse_args()
    if not os.path.exists(args.segments_dir):
        os.mkdir(args.segments_dir)
    sample_rate = args.sr
    input_manifest = open(args.input_manifest)
    all_wavs = input_manifest.readlines()
    if args.num_workers is None:
        args.num_workers = os.cpu_count()
    input_manifest.close()
    all_wavs = check_unique_file_names(all_wavs, args.segments_dir)
    output_manifest = open(args.output_manifest, 'w')

    pool = multiprocessing.Pool(processes=args.num_workers)
    for result in tqdm(pool.imap(func=process, iterable=all_wavs), total=len(all_wavs)):
        if result:
            output_manifest.write(json.dumps(result) + '\n')
    output_manifest.close()


if __name__ == '__main__':
    main()
