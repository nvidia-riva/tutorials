<img src="http://developer.download.nvidia.com/compute/machine-learning/frameworks/nvidia_logo.png" style="width: 90px; float: right;">

# Riva German Data Pipeline

In this tutorial, we will go through the steps to download raw public speech data and proprocess that for NeMo training.

## Data Collection
When adapting Riva to a whole new language, a large amount of high-quality transcribed audio data is critical for training high-quality acoustic models. 

For German, there are several significant sources of public datasets that we can readily leverage:

- [Mozila Common Voice](https://commonvoice.mozilla.org/en/datasets) (MCV) corpus 7.0, `DE` subset: 571 hours 
- [Multilingual LibriSpeech](http://www.openslr.org/94/) (MLS), `DE` subset: 1918 hours
- [Voxpopuli](https://ai.facebook.com/blog/voxpopuli-the-largest-open-multilingual-speech-corpus-for-ai-translation-and-more/), `DE` subset: 214 hours

The total amount of public datasets is thus ~2700 hours of transcribed German speech audio data. 

In addition, to train Riva [world-class models](https://docs.nvidia.com/deeplearning/riva/user-guide/docs/asr/asr-overview.html#language-support), we acquired proprietary datasets, bringing the total number of data to ~3500 hours.

## 2. Data preparation

The data preparation phase carries out a series of preparation steps required to convert the diverse raw audio datasets into a uniform format that can be efficiently digested by NVIDIA NeMo toolkit. These steps are:

### 2.1. Data preprocessing

**Audio data**: Audio data acquired from various sources are inherently heterogeneous (file format, sample rate, bit depth, number of audio channels...). Therefore, as a preprocessing step, we build a separate data ingestion pipeline for each source and convert these audio data to a common format with the following characteristics:
- Wav format
- Bit depth: 16 bits
- Sample rate of 16 Khz
- Single audio channel

**Text data**: 

- Text Normalization converts text from written form into its verbalized form. It is used as a preprocessing step for preprocessing Automatic Speech Recognition (ASR) training transcripts. For German text normalization, we primarily leverage NeMo text normalization [library](https://github.com/NVIDIA/NeMo/tree/main/nemo_text_processing/text_normalization/de). In addition, we also also tried to convert all outdated German word spellings to modern spelling.

Dataset ingestion scripts are used to convert the various datasets into the standard manifest format expected by NeMo. Next, we build a text tokenizer.


**Tokenizer**: There are two popular encoding choices: character encoding and sub-word encoding. Sub-word encoding models are almost nearly identical to the character encoding models. The primary difference lies in the fact that a sub-word encoding model accepts a sub-word tokenized text corpus and emits sub-word tokens in its decoding step. 
Preparation of the tokenizer is made simple by the [process_asr_text_tokenizer.py script](https://github.com/NVIDIA/NeMo/blob/main/scripts/tokenizers/process_asr_text_tokenizer.py) in NeMo. We leverage this script to build the text corpus from the manifest directly, then create a tokenizer using that corpus.



### 2.2. Data cleaning/filtering

This step is carried out to filter out some outlying samples in the datasets. 

- Samples that are too long, too short or empty are filtered out.

- In addition, we also filter out samples that are considered 'noisy', that is, samples having very high WER (word error rate) or CER (character error rate) w.r.t. a previously trained German models. 


### 2.3. Binning

For training ASR models, audios with different lengths may be grouped into a batch. It would make it necessary to use paddings to make all the same length. These extra paddings is a significant source of computation waste. Splitting the training samples into buckets with different lengths and sampling from the same bucket for each batch would increase the computation efficiency. It may result into training speeedup of more than 2X. 

We leverage NeMo conversion [script](https://github.com/NVIDIA/NeMo/blob/v1.0.2/scripts/speech_recognition/convert_to_tarred_audio_dataset.py) to carry out this step.

### 2.4. Train and Test splitting

This step is a staple of the any deep learning and machine learning development pipeline, to ensure that the model is learning to generalize without overfitting the training data. For the test set, we additionally curated data that isn't from the same source as the training datasets, such as Youtube and TED talks.

### 2.5. Tarring

If experiments are run on a cluster with datasets stored on a distributed file system, the user will likely want to avoid constantly reading multiple small files and would prefer tarring their audio files. You can easily convert your existing NeMo-compatible ASR datasets using the conversion [script](https://github.com/NVIDIA/NeMo/blob/v1.0.2/scripts/speech_recognition/convert_to_tarred_audio_dataset.py).
