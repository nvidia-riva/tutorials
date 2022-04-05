# Riva Speech Skills Demo Notebooks

This directory contains demo notebooks for Riva Speech Skills.

## Requirements
Please follow the instructions from [Riva Skills Quick Start Guide](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/riva/resources/riva_quickstart) to deploy the Riva Speech Skills server container before running these notebooks.


## Setup
1. Start the Riva client container
```bash
docker run --init -it \
	--net=host --rm \
	-v $(pwd):/work/notebooks \
	--name riva-client \
	nvcr.io/nvidia/riva/riva-speech-client:1.8.0-beta
```

2. Start a Jupyter session to explore these notebook with
```bash
jupyter notebook --allow-root --ip=0.0.0.0 --notebook-dir=/work/notebooks
```

## Notebooks

- [Riva_speech_API_demo](Riva_speech_API_demo.ipynb).
- [Riva_speech_QA_demo](Riva_speech_QA_demo.ipynb).
