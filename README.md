# Sonic OC Bot

A bot that randomly generates Sonic OCs, fanfictions, and Sonic Says segments.

## Setup

### Package Installation

The easiest way to get set up with this repository is to use [Conda](https://www.anaconda.com/) and install the requirements from there:

```sh
$ CONDA_ENV_NAME=<environment name>
$ conda create --name $CONDA_ENV_NAME --file requirements/<os>/conda.txt --channel conda-forge
$ conda activate $CONDA_ENV_NAME
$ pip install -r requirements/<os>/pip.txt
```

However, nothing is also stopping you from manually installing all the relevant requirements through pip as well 🙂 (ideally in a [venv](https://docs.python.org/3/library/venv.html) or [pipenv](https://pipenv.pypa.io/en/latest/)).

Type and formatting checking are done using `mypy` and `black`, both of which are installed using the above requirements installation.

**Note about GPU Acceleration**: this repo uses Tensorflow to create text generation models. The requirements install takes care of GPU acceleration on macOS for Tensorflow, but if you want GPU acceleration on other platforms, replace `tensorflow` in `requirements/<os>/conda.txt` with `tensorflow-gpu` and make sure you have the proper CUDA/ROCm drivers set up for your system.

### Required Data

This repo requires a good amount of data to run. Please see each of the following guides to see what files are required:

- [Files in /corpus](corpus/CORPUS-README.md)
- [Files in /data](data/DATA-README.md)
- [Files in /fonts](fonts/FONTS-README.md)
- [Files in /images](images/IMAGES-README.md)

The `models` directory doesn't need any data files put into in it; instead, it will contain trained text generation models. This directory contains a Jupyter notebook that will aid in training the models. See below for the file structure of this directory too:

- [Files in /models](models/MODELS-README.md)

You will need to open the Jupyter notebook and then run the cells to train the model. These commands will help you start up Jupyter as long as you installed the requirements earlier and have the Conda environment activated:

```sh
$ cd <repository directory>
$ jupyter lab
```

## Other Documentation

Documentation for the code itself, including classes, lives [here](https://benshoeman.github.io/SonicOCBot/) and is automatically generated on push to master. It's generated using [pdoc](https://pdoc.dev/), which uses docstrings in the functions to create documentation. (This repo is documented using numpydoc format.)
