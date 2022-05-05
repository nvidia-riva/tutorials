import logging
import subprocess
import os
import zipfile
import tarfile

def convert_audio_format(manifest_file: str, out_dir: str, params: dict):
    """
    Audio format conversion to 16-bit 16khz mono wav
    """
    return_code = 0
    script_base_dir = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.join(script_base_dir, "process_audio.py")
    manifest_file_fixed = os.path.splitext(manifest_file)[0] + "_fixed.json"
    try:
        logging.info("Audio conversion running for {0}".format(manifest_file))
        subprocess.check_output("python {} --input_manifest {} --segments_dir {} --output_manifest {} --num_workers {}".format(script_path, manifest_file, out_dir, manifest_file_fixed, params['num_workers']), shell=True)
        subprocess.check_output("mv {} {} ".format(manifest_file_fixed, manifest_file), shell=True)
    except subprocess.CalledProcessError as err:
        logging.error("Error {} returned by command {}. Output: {}".format(err.returncode, err.cmd, err.output))
        return_code = 1
    return return_code

def unzip_dataset_archive(zipfile_path: str, unzipped_dir: str):
    """
    Unzip dataset archive to unzipped_dir
    """
    return_code = 0
    try:
        logging.info("Unzipping dataset archive from {} to {}".format(zipfile_path, unzipped_dir))
        with zipfile.ZipFile(zipfile_path, 'r') as zip_ref:
            zip_ref.extractall(unzipped_dir)
    except zipfile.BadZipfile:
        logging.error("Unzip error for {}".format(zipfile_path))
        return_code = 1
    return return_code

def untar_dataset_archive(tarfile_path: str, untarred_dir: str):
    """
    Untar dataset archive to untarred_dir
    """
    return_code = 0
    try:
        logging.info("Untarring dataset archive from {} to {}".format(tarfile_path, untarred_dir))
        tar = tarfile.open(tarfile_path)
        tar.extractall(untarred_dir)
        tar.close()
    except tarfile.TarError:
        logging.error("Untar error for {}".format(tarfile_path))
        return_code = 1
    return return_code

def clean(clean_dir: str):
    """
    Clean temporary directory to avoid disk overusage
    """
    return_code = 0
    try:
        logging.info("Cleaning directory: {}".format(clean_dir))
        subprocess.check_output("rm -rf {}".format(clean_dir), shell=True)
    except subprocess.CalledProcessError as err:
        logging.error("Error {} returned by command {}. Output: {}".format(err.returncode, err.cmd, err.output))
        return_code = 1
    return return_code
    