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
| ASR | The Making of RIVA German ASR Service | ASR, New Language Adaptation, German | [Riva ASR - German](New-language-adaptation/German) | 
| ASR | The Making of RIVA Hindi ASR Service | ASR, New Language Adaptation, Hindi | [Riva ASR - Hindi](New-language-adaptation/Hindi) | 
| ASR | The Making of RIVA Mandarin ASR Service | ASR, New Language Adaptation, Mandarin | [Riva ASR - Mandarin](New-language-adaptation/Mandarin) | 
| Deploy | How to Deploy Riva at Scale on AWS with EKS | Deploy, AWS EKS | [Riva - Deploy - AWS EKS](deploy-eks.md) |
| TTS | How do I use Riva TTS APIs with out-of-the-box models? | TTS, API Basics | [Riva TTS - API Basics](tts-python-basics.ipynb) |
| TTS | How do I customize Riva TTS audio output with SSML? | TTS, Customization, SSML, Pitch, Rate, Pronunciation | [Riva TTS - Customization with SSML](tts-python-advanced-customizationwithssml.ipynb) |

## Requirements and Setup

### Running the NVIDIA Riva Tutorials
This section covers the Requirements and Setup needed to run all Riva Tutorials, except:  
1. [How to improve accuracy on specific speech patterns by fine-tuning the Acoustic Model (Citrinet) in the Riva ASR pipeline](asr-python-advanced-finetune-am-citrinet-for-noisy-audio-withtao.ipynb): For the Requirements and Setup of this tutorial, please refer to this section.  


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

### Running the NVIDIA Riva Tutorial "How to improve accuracy on specific speech patterns by fine-tuning the Acoustic Model (Citrinet) in the Riva ASR pipeline"

#### Requirements  
Before you try running this NVIDIA Riva tutorials, ensure you meet the following requirements: 
- docker 

#### Setup  
1. Clone NVIDIA NeMo repository.  
``git clone -b main https://github.com/NVIDIA/NeMo.git``

2. Clone the NVIDIA Riva tutorials repository.  
``git clone https://github.com/nvidia-riva/tutorials.git``  
``cd tutorials``  

3. Pull and run NVIDIA NeMo container.  
``docker run -it --rm -v <nemo_github_folder>:/NeMo -v $PWD:/tutorials --net=host nvcr.io/nvidia/pytorch:22.04-py3``  
``cd /tutorials``  

4. Install ffmpeg library.  
``apt-get update && apt-get install -y ffmpeg``  

5. Start the Jupyter notebooks server.  
``jupyter notebook --allow-root --port 8888``  
If you have a browser installed on your machine, the notebook should automatically open. If you do not have a browser, copy/paste the URL from the command.  


### Running the Riva Client

#### Requirements
Before you try running the Riva client, ensure you meet the following requirements: 
- You have access and are logged into NVIDIA NGC. For step-by-step instructions, refer to the [NGC Getting Started Guide](https://docs.nvidia.com/ngc/ngc-overview/index.html#registering-activating-ngc-account).
- [Python 3](https://www.python.org/download/releases/3.0/) 

#### Setup
1. Download the Riva Quick Start scripts, if not already done. `x.y.z` is the Riva Speech Skills version number - The latest Riva version number can be found in the [Riva Quick Start Guide](https://docs.nvidia.com/deeplearning/riva/user-guide/docs/quick-start-guide.html#)'s [Local Deploymnent using Quick Start Scripts section](https://docs.nvidia.com/deeplearning/riva/user-guide/docs/quick-start-guide.html#local-deployment-using-quick-start-scripts)
``ngc registry resource download-version "nvidia/riva/riva_quickstart:<x.y.z>"``

2. [Optional] If using the `venv-riva-tutorials` (or another) Python virtual environment, activate it.  
``. <Python virtual environment directory location>/venv-riva-tutorials/bin/activate``

3. Install the Riva client library.  
``cd riva_quickstart_v<x.y.z>``  
``pip install riva_api-<x.y.z>-py3-none-any.whl``

## Copyright and License
Copyright 2022 NVIDIA Corporation. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0). Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
