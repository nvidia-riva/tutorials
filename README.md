<img src="http://developer.download.nvidia.com/notebooks/dlsw-notebooks/riva_all_tutorials-readme/nvidia_logo.png" style="width: 90px; float: right;">

# Riva Speech Skills Tutorials

The best way to get started with Riva is to start with the tutorials.

## Tutorials

| Domain | Tutorial | Key Words | Github URL |
|--------|----------|-----------|------------|
| ASR | How do I use Riva ASR APIs with out-of-the-box models? | ASR, API Basics | [Riva ASR - API Basics](asr-python-basics.ipynb) |
| ASR | How to Improve Recognition of Specific Words | ASR, Customization | [Riva ASR - Customization Overview](asr-how-to-improve-recognition-for-specific-words.md) |
| ASR | How do I boost specific words at runtime with word boosting? | ASR, Customization, Word Boosting | [Riva ASR - Customization - Word Boosting](asr-python-advanced-wordboosting.ipynb) |
| ASR | How to Customize Riva ASR Vocabulary and Pronunciation with Lexicon Mapping | ASR, Customization, Custom Vocab, Lexicon Mapping | [Riva ASR - Customization - Vocab and Lexicon Mapping](asr-python-advanced-customize-vocabulary-and-lexicon.ipynb) |
| ASR | How to pretrain a Riva ASR Language Modeling (n-gram) with TAO Toolkit | ASR, Customization, Language Model pretraining, n-gram, TAO Toolkit | [Riva ASR - Customization - Language Model (n-gram) pretraining with TAO Toolkit](asr-python-advanced-tao-ngram-pretrain.ipynb) |
| ASR | How to fine-tune a Riva ASR Acoustic Model (Citrinet) with TAO Toolkit | ASR, Customization, Acoustic Model fine-tuning, Citrinet, TAO Toolkit | [Riva ASR - Customization - Acoustic Model (Citrinet) fine-tuning with TAO Toolkit](asr-python-advanced-finetune-am-citrinet-tao-finetuning.ipynb) |
| ASR | How to deploy custom Acoustic Model (Citrinet) trained with TAO Toolkit on Riva | ASR, Customization, Acoustic Model deployment, Citrinet | [Riva ASR - Customization - Acoustic Model (Citrinet) deployment on Riva](asr-python-advanced-finetune-am-citrinet-tao-deployment.ipynb) |
| ASR | The Making of RIVA German ASR Service | ASR, New Language Adaptation, German | [Riva ASR - German](New-language-adaptation/German) |
| ASR | The Making of RIVA Hindi ASR Service | ASR, New Language Adaptation, Hindi | [Riva ASR - Hindi](New-language-adaptation/Hindi) |
| ASR | The Making of RIVA Mandarin ASR Service | ASR, New Language Adaptation, Mandarin | [Riva ASR - Mandarin](New-language-adaptation/Mandarin) |
| TTS | How do I use Riva TTS APIs with out-of-the-box models? | TTS, API Basics, Customization, SSML, Pitch, Rate, Pronunciation, emphasis, sub | [Riva TTS - API Basics and Customization with SSML](tts-python-basics-and-customization-with-ssml.ipynb) |
| TTS | How to Deploy a custom TTS Models (FastPitch and HiFi-GAN) trained with TAO Toolkit Riva | TTS, Customization, FastPitch, HiFiGAN, Deployment | [Riva TTS - Customization - FastPitch and HiFiGAN deployment on Riva](tts-python-tao-deployment.ipynb) |
| Deploy | How to Deploy Riva at Scale on AWS with EKS | Deploy, AWS EKS | [Riva - Deploy - AWS EKS](deploy-eks.md) |

## Requirements and Setup

### Running the NVIDIA Riva Tutorials
This section covers the Requirements and Setup needed to run all Riva Tutorials.

#### Requirements
Before you try running the NVIDIA Riva tutorials, ensure you meet the following requirements:
- [Python 3](https://www.python.org/download/releases/3.0/)

#### Setup
1. Clone the NVIDIA Riva tutorials repository.
``git clone https://github.com/nvidia-riva/tutorials.git``
``cd tutorials``

2. Create a Python virtual environment - We will be using this virtual environment to install all the depencies needed for Riva tutorials.
``python3 -m venv venv-riva-tutorials``

3. Activate the Python virtual environment we just created.
``. venv-riva-tutorials/bin/activate``

4. Install Jupyter notebook.
``pip3 install jupyter``

5. Create an IPython kernel - The Riva tutorials Jupyter notebooks will be using this kernel in the next step.
``ipython kernel install --user --name=venv-riva-tutorials``

6. Start the Jupyter notebooks server.
``jupyter notebook --allow-root --port 8888``
If you have a browser installed on your machine, the notebook should automatically open. If you do not have a browser, copy/paste the URL from the command.
Once you open a Riva tutorial notebook on a browser, choose the `venv-riva-tutorials` kernel by `Kernel` -> `Change kernel` -> `venv-riva-tutorials`

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

Alternatively, you can install from source [nvidia-riva/python-clients](https://github.com/nvidia-riva/python-clients).

## Copyright and License
Copyright 2022 NVIDIA Corporation. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0). Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
