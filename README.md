<img src="http://developer.download.nvidia.com/notebooks/dlsw-notebooks/riva_all_tutorials-readme/nvidia_logo.png" style="width: 90px; float: right;">

# Riva Speech Skills Tutorials

The best way to get started with Riva is to start with the tutorials.

## Tutorials

| Domain | Tutorial | Key Words | Github URL |
|--------|----------|-----------|------------|
| ASR    | How to use Riva ASR APIs with Out-Of-The-Box Models | ASR, API Basics | [Riva ASR - API Basics](asr-basics.ipynb) |
| ASR    | How to Customize Riva ASR Vocabulary and Pronunciation with Lexicon Mapping | ASR, Customization, Custom Vocab, Lexicon Mapping | [Riva ASR - Customization - Vocab and Lexicon Mapping](asr-customize-vocabulary-and-lexicon.ipynb) |
| ASR    | How to Deploy a Custom Language Model (n-gram) Trained with NVIDIA NeMo on Riva | ASR, Customization, Custom Language Model Deployment, n-gram | [Riva ASR - Customization - Custom Language Model (n-gram) Deployment on Riva](asr-deploy-am-and-ngram-lm.ipynb) |
| ASR    | How to Deploy a Custom Acoustic Model (Citrinet) Trained with NVIDIA NeMo on Riva | ASR, Customization, Acoustic Model Deployment, Citrinet | [Riva ASR - Customization - Acoustic Model (Citrinet) Deployment on Riva](asr-deploy-citrinet.ipynb) |
| ASR    | How to Deploy a custom Acoustic Model (Conformer-CTC) Trained with NVIDIA NeMo on Riva | ASR, Customization, Acoustic Model Deployment, Conformer-CTC | [Riva ASR - Customization - Acoustic Model (Conformer-CTC) Deployment on Riva](asr-deploy-conformer-ctc.ipynb) |
| ASR    | How to Customize a Riva ASR Acoustic Model (Conformer-CTC) with Adapters using NVIDIA NeMo | ASR, Customization, Acoustic Model Fine-Tuning, Adapters, NVIDIA NeMo | [Riva ASR - Customization - Adapters - Acoustic Model Fine-Tuning with NVIDIA NeMo](asr-finetune-conformer-ctc-adapter-nemo.ipynb) |
| ASR    | How to Fine-Tune a Riva ASR Acoustic Model (Conformer-CTC) with NVIDIA NeMo | ASR, Customization, Acoustic Model Fine-Tuning, NVIDIA NeMo | [Riva ASR - Customization - Acoustic Model Fine-Tuning with NVIDIA NeMo](asr-finetune-conformer-ctc-nemo.ipynb) |
| ASR    | How to Improve Recognition of Specific Words | ASR, Customization | [Riva ASR - Customization Overview](asr-improve-recognition-for-specific-words.md) |
| ASR    | How to Improve the Accuracy on Noisy Speech by Fine-Tuning the Acoustic Model (Conformer-CTC) in the Riva ASR Pipeline | ASR, Accuracy, Acoustic Model Fine-Tuning | [Riva ASR - Improve Accuracy - Fine-Tuning the Acoustic Model (Conformer-CTC) in ASR Pipeline](asr-noise-augmentation.ipynb) |
| ASR    | How to Fine-Tune a Riva ASR Acoustic Model (Conformer-CTC) with TAO Toolkit | ASR, Acoustic Model Fine-Tuning, Conformer-CTC | [Riva ASR - Fine-Tune Acoustic Model (Conformer-CTC)](asr-python-advanced-finetune-am-conformer-ctc-tao-finetuning-librispeech-nigerian.ipynb) |
| ASR    | How to Pretrain a Riva ASR Language Modeling (n-gram) with TAO Toolkit | ASR, Customization, Language Model Pretraining, n-gram, TAO Toolkit | [Riva ASR - Customization - Language Model (n-gram) Pretraining with TAO Toolkit](asr-python-advanced-tao-ngram-pretrain.ipynb) |
| ASR    | How to Boost Specific Words at Runtime with Word Boosting | ASR, Customization, Word Boosting | [Riva ASR - Customization - Word Boosting](asr-wordboosting.ipynb) |
| ASR    | The Making of RIVA German ASR Service | ASR, New Language Adaptation, German | [Riva ASR - German](New-language-adaptation/German) |
| ASR    | The Making of RIVA Hindi ASR Service | ASR, New Language Adaptation, Hindi | [Riva ASR - Hindi](New-language-adaptation/Hindi) |
| ASR    | The Making of RIVA Mandarin ASR Service | ASR, New Language Adaptation, Mandarin | [Riva ASR - Mandarin](New-language-adaptation/Mandarin) |
| Deploy | How to Deploy Riva at Scale on AWS with EKS | Deploy, AWS EKS | [Riva - Deploy - AWS EKS](deploy-eks.md) |
| TTS    | How to use Riva TTS APIs with Out-Of-The-Box Models | TTS, API Basics, Customization, SSML, Pitch, Rate, Pronunciation, Emphasis, Sub | [Riva TTS - API Basics and Customization with SSML](tts-basics-customize-ssml.ipynb) |
| TTS    | TTS Deploy | TTS, Deployment | [Riva TTS - Deployment on TTS](tts-deploy.ipynb) |
| TTS    | Evaluate a TTS Pipeline | TTS, Evaluate Pipeline | [Riva TTS - Evaluate a TTS Pipeline](tts-evaluate.ipynb) |
| TTS    | TTS Fine-Tune using NeMo | TTS, Fine-Tuning, NVIDIA NeMo | [Riva TTS - Fine-Tuning using NeMo](tts-finetune-nemo.ipynb) |
| TTS    | Calculate and Plot the Distribution of Phonemes in a TTS Dataset | TTS, Phonemes | [Riva TTS - Phonemes in a TTS Dataset](tts-phoneme-distribution.ipynb) |



## Requirements and Setup

### Running the NVIDIA Riva Tutorials
This section covers the requirements and setup needed to run all Riva tutorials.

#### Requirements
Before you try running the NVIDIA Riva tutorials, ensure you meet the following requirements:
- [Python 3](https://www.python.org/download/releases/3.0/)

#### Setup
1. Clone the NVIDIA Riva tutorials repository.
``git clone https://github.com/nvidia-riva/tutorials.git``
``cd tutorials``

2. Create a Python virtual environment. We will use this virtual environment to install all the dependencies needed for the Riva tutorials.
``python3 -m venv venv-riva-tutorials``

3. Activate the Python virtual environment we just created.
``. venv-riva-tutorials/bin/activate``

4. Install Jupyter notebook.
``pip3 install jupyter``

5. Create an IPython kernel. The Riva tutorials Jupyter notebooks will use this kernel in the next step.
``ipython kernel install --user --name=venv-riva-tutorials``

6. Start the Jupyter notebooks server.
``jupyter notebook --allow-root --port 8888``

If you have a browser installed on your machine, the notebook should automatically open. If you do not have a browser, copy/paste the URL from the command.
Once you open a Riva tutorial notebook on a browser, choose the `venv-riva-tutorials` kernel by `Kernel` -> `Change kernel` -> `venv-riva-tutorials`.

### Running the Riva Client

#### Requirements
Before you try running the Riva client, ensure you meet the following requirements:
- You have access and are logged into NVIDIA NGC. For step-by-step instructions, refer to the [NGC Getting Started Guide](https://docs.nvidia.com/ngc/ngc-overview/index.html#registering-activating-ngc-account).
- [Python 3](https://www.python.org/download/releases/3.0/)

#### Setup

1. [Optional] If using the `venv-riva-tutorials` (or another) Python virtual environment, activate it.
``. <Python virtual environment directory location>/venv-riva-tutorials/bin/activate``

2. Install `nvidia-riva-client` using `pip`.
```bash
pip install nvidia-riva-client
```

Alternatively, you can install it from the source; [nvidia-riva/python-clients](https://github.com/nvidia-riva/python-clients).

## Copyright and License
Copyright 2023 NVIDIA Corporation. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0). Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
