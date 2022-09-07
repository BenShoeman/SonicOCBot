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

Type and formatting checking are done using `mypy` and `black`, both of which are installed using the above requirements installation. Unused imports are checked with `unimport`, also installed with the above instructions.

### Required Data

This repo requires a good amount of data to run. Please see each of the following guides to see what files are required:

- [Files in /corpus](corpus/CORPUS-README.md)
- [Files in /data](data/DATA-README.md)
- [Files in /fonts](fonts/FONTS-README.md)
- [Files in /images](images/IMAGES-README.md)

The `models` directory doesn't need any data files put into in it; instead, it will contain trained text generation models generated using [`train.py`](/train.py). See below for the file structure of this directory:

- [Files in /models](models/MODELS-README.md)

## Documentation on the Code

[Documentation for the code itself lives here](https://benshoeman.github.io/SonicOCBot/) and is automatically generated on push to `master`. It's generated using [pdoc](https://pdoc.dev/), which uses docstrings in the functions to create documentation. (This repo is documented using numpydoc format.)
