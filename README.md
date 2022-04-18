# WIP - Riva Speech Skills Tutorials

This directory contains tutorials for Riva Speech Skills.

## Tutorials

- [Riva ASR - How to use Riva ASR APIs (with OOTB models)](asr-python-basics.ipynb)
- [Riva ASR - How to boost specific words at run-time - Ex: Contact List, Meeting participants](asr-python-advanced-wordboosting.ipynb)
- [Riva TTS - How to use Riva TTS APIs (with OOTB models)](tts-python-basics.ipynb)
- [Riva TTS - How to customize TTS audio output with SSML](tts-python-advanced-customizationwithssml.ipynb)

## Requirements and Setup

### Running the NVIDIA Riva Tutorials

#### Requirements
1. You need to have Python3 installed 

#### Setup:
1. Clone the NVIDIA Riva Tutorials repository  
``git clone https://github.com/nvidia-riva/tutorials.git``
``cd tutorials``

2. Install and run Jupyter Notebooks server  
``pip install jupyter``  
``jupyter notebook --allow-root --port 8888``  
If you have a browser installed on your machine, it should automatically open up. Else copy-paste the url from the command

### Riva Client:

#### Requirement:
1. You have access and are logged into NVIDIA NGC. For step-by-step instructions, refer to the NGC Getting Started Guide.
2. You need to have Python3 installed 

#### Setup:
1. Download Riva QSG (If not already done)
``ngc registry resource download-version "nvidia/riva/riva_quickstart:2.0.0"``
2. Install Riva Client Library
``cd riva_quickstart_v2.0.0``
``pip install riva_api-2.0.0-py3-none-any.whl``

### TAO Toolkit:

#### Requirement:
1. Refer to [this page](https://docs.nvidia.com/tao/tao-toolkit/text/tao_toolkit_quick_start_guide.html#hardware) for Hardware requirements for TAO
2. Refer to [this page](https://docs.nvidia.com/tao/tao-toolkit/text/tao_toolkit_quick_start_guide.html#software-requirements) for Software requirements for TAO. If you do not meet the software requirements, refer to [this page](https://docs.nvidia.com/tao/tao-toolkit/text/tao_toolkit_quick_start_guide.html#installing-the-pre-requisites) for installing pre-requisites.

#### Setup:
Refer to [this page](https://docs.nvidia.com/tao/tao-toolkit/text/tao_toolkit_quick_start_guide.html#installing-tao-toolkit) to install TAO Toolkit

## License