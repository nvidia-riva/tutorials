<img src="http://developer.download.nvidia.com/compute/machine-learning/frameworks/nvidia_logo.png" style="width: 90px; float: right;">

# German ASR Pipeline Deployment

In this tutorial, we are going through the steps to deploy a German ASR pipeline into production. Refer to the [deployment.ipynb](deployment.ipynb) notebook for an interactive version of this guide.

## Model checklist
This tutorial assumes that you have the following models ready:

- An acoustic model
- A language model (optional)
- An inverse text normalization model (optional)
- A punctuation and capitalization model (optional)

## Pre requisite

- Make sure you have access to [NGC](https://ngc.nvidia.com) to download models with the [NGC CLI tool](https://docs.ngc.nvidia.com/cli).  

- Download Riva quickstart scripts to a local directory <RIVA_QUICKSTART_DIR>:

```bash
ngc registry resource download-version nvidia/riva/riva_quickstart:2.1.0
```

- Prepare a local folder `<RIVA_MODEL_DIR>` to download models to.

- Prepare a local folder `<RIVA_MODEL_REPO>` to store deployed Riva models.

### BYO models
If bringing your own models, refer to the [training](./training) section of this guide for details on how to train your own custom models.

### Pre-trained models

Alternatively, you can deploy pre-trained models. All Riva German assets are published on [NGC](https://ngc.nvidia.com) (including `.nemo`, `.riva`, `.tlt` and `.rmir` assets). You can use these models as starting points for your development or for deployment as-is.

Download the following models, either via the web interface or via the NGC CLI tool to the `<RIVA_MODEL_DIR>` directory.

**Acoustic models**:
Select either:
- Citrinet ASR German:     
    - Download [Nemo version (.nemo format)](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/nemo/models/stt_de_citrinet_1024) with 
    
```bash
    ngc registry model download-version "nvidia/nemo/stt_de_citrinet_1024:1.5.0"
```
- Conformer ASR German
    - [Nemo version (.nemo format)](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/nemo/models/stt_de_conformer_ctc_large)

```bash
    ngc registry model download-version "nvidia/nemo/stt_de_conformer_ctc_large:1.5.0_lm"
```
    
**Inverse text normalization models**: This model is an [OpenFST finite state archive (.far)](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/tao/models/inverse_normalization_de_de) for use within the opensource Sparrowhawk normalization engine and Riva.   

```bash
ngc registry model download-version "nvidia/tao/inverse_normalization_de_de:deployable_v1.0"
```

**Language model**:  These models are simple [4-gram language models](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/tao/models/speechtotext_de_de_lm) trained with Kneser-Ney smoothing using KenLM. This directory also contains the decoder dictionary used by the Flashlight decoder.

```bash
ngc registry model download-version "nvidia/tao/speechtotext_de_de_lm:deployable_v2.0"
```

**Punctuation and capitalization model:** [Riva Punctuation and Capitalization model for German](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/tao/models/punctuationcapitalization_de_de_bert_base). 

```bash
ngc registry model download-version "nvidia/tao/punctuationcapitalization_de_de_bert_base:trainable_v1.0"
```

## Preparing Models 

### Nemo to Riva conversion

Start Nemo container:
```bash
docker run --rm -it $PWD/:/models nvcr.io/nvidia/nemo:22.01 bash

cd <RIVA_QUICKSTART_DIR>
pip3 install nvidia-pyindex
pip3 install nemo2riva-2.0.0-py3-none-any.whl
```

Converting acoustic model to Nemo format.
```bash
nemo2riva --out /models/stt_de_citrinet_1024_v1.5.0/stt_de_citrinet_1024.riva /models/stt_de_citrinet_1024_v1.5.0/stt_de_citrinet_1024.nemo --max-dim=100000
```

### Making service 

The ServiceMaker container is responsible for preparing models for deployment. Start an interactive session with:

```bash
docker pull nvcr.io/nvidia/riva/riva-speech:2.0.0-servicemaker
docker run --gpus all -it --rm \
     -v <RIVA_MODEL_DIR>:/servicemaker-dev \
     -v <RIVA_REPO_DIR>:/data \
     --entrypoint="/bin/bash" \
     nvcr.io/nvidia/riva/riva-speech:2.0.0-servicemaker
```

#### Build and deploy an offline ASR pipeline
The ASR pipeline including the acoustic model, language model and inverse text normalization model is built as follows: 

```bash
riva-build speech_recognition -f \
   /servicemaker-dev/citrinet-1024-de-DE-asr-offline.rmir /servicemaker-dev/stt_de_citrinet_1024_v1.5.0/stt_de_citrinet_1024.riva \
   --offline \
   --name=citrinet-1024-de-DE-asr-offline \
   --ms_per_timestep=80 \
   --featurizer.use_utterance_norm_params=False \
   --featurizer.precalc_norm_time_steps=0 \
   --featurizer.precalc_norm_params=False \
   --chunk_size=900 \
   --left_padding_size=0. \
   --right_padding_size=0. \
   --decoder_type=flashlight \
   --decoding_language_model_binary=/servicemaker-dev/speechtotext_de_de_lm_vdeployable_v2.0/riva_de_asr_set_2.0_4gram.binary \
   --decoding_vocab=/servicemaker-dev/speechtotext_de_de_lm_vdeployable_v2.0/dict_vocab.txt \
   --flashlight_decoder.lm_weight=0.2 \
   --flashlight_decoder.word_insertion_score=0.2 \
   --flashlight_decoder.beam_threshold=20. \
   --wfst_tokenizer_model=/servicemaker-dev/inverse_normalization_de_de_vdeployable_v1.0/tokenize_and_classify.far \
   --wfst_verbalizer_model=/servicemaker-dev/inverse_normalization_de_de_vdeployable_v1.0/verbalize.far \
   --language_code=de-DE


riva-deploy -f /servicemaker-dev/citrinet-1024-de-DE-asr-offline.rmir /data/models
```

The `riva-build` command takes in an acoustic model in `.riva` format, the inverse text normalization models in `.far` format, and a n-gram binary language model file.

Note: See Riva documentation for build commands for streaming ASR services.

#### Build and deploy and punctuation and capitalization model

When doing ASR, the Riva server will look for a punctuator model that matches the language in the ASR request config.
The punctuator model can be built and deployed with:

```bash
riva-build punctuation -f \
   /servicemaker-dev/de_punctuation_1_0.rmir  \
   /servicemaker-dev/punctuationcapitalization_de_de_bert_base_vdeployable_v1.0/de_punctuation_1_0.riva \
   --language_code=de-DE

riva-deploy -f /servicemaker-dev/de_punctuation_1_0.rmir /data/models 
```

## Start Riva server

That concludes the building and deployment of the Riva German ASR service. Now you can start the Riva server.