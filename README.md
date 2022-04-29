# Riva Speech Skills Tutorials

This directory contains tutorials for Riva Speech Skills.

## Tutorials

- [Riva ASR - How to use Riva ASR APIs (with OOTB models)](asr-python-basics.ipynb)
- [Riva ASR - How to boost specific words at run-time - Ex: Contact List, Meeting participants](asr-python-advanced-wordboosting.ipynb)
- [Riva ASR - How to improve recognition for specific words](asr-how-to-improve-recognition-for-specific-words.md)
- [Riva TTS - How to use Riva TTS APIs (with OOTB models)](tts-python-basics.ipynb)
- [Riva TTS - How to customize TTS audio output with SSML](tts-python-advanced-customizationwithssml.ipynb)


## Requirements and Setup

### Running the NVIDIA Riva Tutorials

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
1. Download the Riva Quick Start scripts, if not already done.  
``ngc registry resource download-version "nvidia/riva/riva_quickstart:2.0.0"``

2. [Optional] If using the `venv-riva-tutorials` (or another) Python virtual environment, activate it.  
``. <Python virtual environment directory location>/venv-riva-tutorials/bin/activate``

3. Install the Riva client library.  
``cd riva_quickstart_v2.0.0``  
``pip install riva_api-2.0.0-py3-none-any.whl``

## Copyright and License
Copyright 2022 NVIDIA Corporation. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0). Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
