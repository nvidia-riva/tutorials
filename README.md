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
Before you try running the NVIDIA Riva tutorials, ensure you meet the following requirements: 
- [Python 3](https://www.python.org/download/releases/3.0/) 

#### Setup
1. Clone the NVIDIA Riva tutorials repository.  
``git clone https://github.com/nvidia-riva/tutorials.git``
``cd tutorials``

2. Install and run the Jupyter notebooks server.  
``pip install jupyter``  
``jupyter notebook --allow-root --port 8888``  
If you have a browser installed on your machine, the notebook should automatically open. If you do not have a browser, copy/paste the URL from the command.

### Running the Riva Client

#### Requirements
- You have access and are logged into NVIDIA NGC. For step-by-step instructions, refer to the [NGC Getting Started Guide](https://docs.nvidia.com/ngc/ngc-overview/index.html#registering-activating-ngc-account).
- [Python 3](https://www.python.org/download/releases/3.0/) 

#### Setup
1. Download the Riva Quick Start scripts, if not already done. 
``ngc registry resource download-version "nvidia/riva/riva_quickstart:2.0.0"``
2. Install the Riva client library.
``cd riva_quickstart_v2.0.0``
``pip install riva_api-2.0.0-py3-none-any.whl``

### TAO Toolkit:

#### Requirements
- Refer to [this page](https://docs.nvidia.com/tao/tao-toolkit/text/tao_toolkit_quick_start_guide.html#hardware) for hardware requirements for TAO Toolkit.
- Refer to [this page](https://docs.nvidia.com/tao/tao-toolkit/text/tao_toolkit_quick_start_guide.html#software-requirements) for software requirements for TAO Toolkit. If you do not meet the software requirements, refer to [this page](https://docs.nvidia.com/tao/tao-toolkit/text/tao_toolkit_quick_start_guide.html#installing-the-pre-requisites) for installing the prerequisites.

#### Setup:
Refer to [this page](https://docs.nvidia.com/tao/tao-toolkit/text/tao_toolkit_quick_start_guide.html#installing-tao-toolkit) to install TAO Toolkit.

## License