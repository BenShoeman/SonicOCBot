# Sonic OC Bot

A bot that randomly generates Sonic OCs, fanfictions, and Sonic Sez segments, which can be found [@SonicOCBot](https://twitter.com/SonicOCBot) on Twitter!

## Setup

### Package Installation

The easiest way to get set up with this repository is to use [Conda](https://www.anaconda.com/) and install the requirements from there:

```sh
$ CONDA_ENV_NAME=<environment name>
$ conda create --name $CONDA_ENV_NAME --file requirements-conda.txt --channel conda-forge
$ conda activate $CONDA_ENV_NAME
$ pip3 install -r requirements-pip.txt
```

However, nothing is also stopping you from manually installing all the relevant requirements through pip as well 🙂 (ideally in a [venv](https://docs.python.org/3/library/venv.html) or [pipenv](https://pipenv.pypa.io/en/latest/)).

Type and formatting checking are done using `mypy` and `black`, both of which are installed using the above requirements installation.

A Chromium-based web browser is also a requirement if you want to run the scrapers, for Selenium. You *may* also need to change the `browser` parameter in the `Html2Image` constructor if you are having problems with it (this is present in the file `src/util/MDtoImage.py`).

**Note about GPU Acceleration**: this repo uses Tensorflow to create text generation models. If you want GPU acceleration, replace `tensorflow` in `requirements-conda.txt` with `tensorflow-gpu` and make sure you have the proper CUDA/ROCm drivers set up for your system. This repo also uses ONNX to run inference from these models. If you want GPU acceleration for that, add `onnxruntime-gpu` in the `requirements-pip.txt` file (NOT `requirements-conda.txt` -- this causes issues with the `nnsplit` module).

**Note about Minimal Requirements Files**: There are two other conda and pip install requirements files labeled `requirements-*-min.txt`. These only include the dependencies needed for running the main application (`main.py` and everything under the `src` directory).

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
