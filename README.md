# Sonic OC Bot

A bot that randomly generates Sonic OCs, fanfictions, and Sonic Says segments.

## Setup

### Requirements

- Python 3.9+ (only tested on 3.9 and 3.10 but any higher version should work, maybe with some dependency version tweaks)

### Package Installation

Install the requirements from [`/requirements`](/requirements/) and you should be good to go:

```sh
cd SonicOCBot  # ... wherever you have the repo stored
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/minimal.txt # or full.txt if running notebooks
playwright install # installs playwright requirements
```

This also uses [Ollama](https://github.com/ollama/ollama) to run some text generation; follow the instructions there to set it up. You can also disable it by removing `Ollama` in `_MODEL_PROBABILITIES` in [the `ModelMap` module](src/TextModel/ModelMap.py), and setting the `Markov` probability to 1.0.

### Quality Checks

This repo uses `mypy`, `black`, and `unimport` to check typing, formatting, and unused imports on a PR. All are installed during the above requirements installation and you can run all the checks using [`quality-check.sh`](/quality-check.sh).

### Required Data

This repo requires some data to generate images. Please see each of the following guides to see what files are required:

- [`/data`](/data/DATA-README.md)
- [`/fonts`](/fonts/FONTS-README.md)
- [`/images`](/images/IMAGES-README.md)
- [`/models`](/models/MODELS-README.md)
- [`/templates`](/templates/TEMPLATES-README.md)

Note that the `models` directory requires trained models to be put into it. These are generated from text files using [`train.py`](/train.py).

## [Code Documentation](https://benshoeman.github.io/SonicOCBot/)

Documentation for the code itself lives [here](https://benshoeman.github.io/SonicOCBot/) and is automatically generated on push to `master`. It's generated using [pdoc](https://pdoc.dev/), which uses docstrings in the functions to create documentation. (This repo is documented using numpydoc format.)
