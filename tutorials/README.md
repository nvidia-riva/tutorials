# Riva Speech Skills Tutorials

This directory contains tutorials for Riva Speech Skills.

## Tutorials

- [Riva ASR - How to use Riva ASR APIs (with OOTB models)](asr-python-basics.ipynb)
- [Riva ASR - How to boost specific words at run-time - Ex: Contact List, Meeting participants](asr-python-advanced-wordboosting.ipynb)
- [Riva TTS - How to use Riva TTS APIs (with OOTB models)](tts-python-basics.ipynb)
- [Riva TTS - How to customize TTS audio output with SSML](tts-python-advanced-customizationwithssml.ipynb)

## Requirements and Setup

### Setup to run Jupyter Notebook
pip3 install jupyter  
jupyter notebook --ip=0.0.0.0 --allow-root --port 8888

### Riva Client:

#### Requirement:
Please follow the instructions from [Riva Skills Quick Start Guide](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/riva/resources/riva_quickstart) to deploy the Riva Speech Skills server container before running these notebooks.

#### Setup:
ngc registry resource download-version "nvidia/riva/riva_quickstart:2.0.0"
cd riva_quickstart_v2.0.0
pip install riva_api-2.0.0-py3-none-any.whl

### TAO:

#### Requirement:
https://docs.nvidia.com/tao/tao-toolkit/text/tao_toolkit_quick_start_guide.html#hardware  
https://docs.nvidia.com/tao/tao-toolkit/text/tao_toolkit_quick_start_guide.html#software-requirements  
https://docs.nvidia.com/tao/tao-toolkit/text/tao_toolkit_quick_start_guide.html#installing-the-pre-requisites

#### Setup:
https://docs.nvidia.com/tao/tao-toolkit/text/tao_toolkit_quick_start_guide.html#installing-tao-toolkit

## License