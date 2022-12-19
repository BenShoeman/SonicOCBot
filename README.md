# Sonic OC Bot

A bot that randomly generates Sonic OCs, fanfictions, and Sonic Says segments.

## Setup

### Package Installation

Install the requirements from [`/requirements`](/requirements/), choosing the right file for your OS, and you should be good to go:

```sh
cd SonicOCBot  # ... wherever you have the repo stored
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/local.txt
```

This repo uses `mypy`, `black`, and `unimport` to check typing, formatting, and unused imports respectively. All are installed during the above requirements installation and you can run all the checks using [`quality-check.sh`](/quality-check.sh).

As this repo uses the `html2image` module, this repo requires a Chromium browser to generate the images. The module should detect the browser if it's Chrome or Chromium, but if not, set the `CHROME_BIN` environment variable to the path of the executable and that will be used.

### Required Data

This repo requires a good amount of data to run. Please see each of the following guides to see what files are required:

- [Files in /data](/data/DATA-README.md)
- [Files in /fonts](/fonts/FONTS-README.md)
- [Files in /images](/images/IMAGES-README.md)
- [Files in /models](/models/MODELS-README.md)
- [Files in /templates](/templates/TEMPLATES-README.md)

Note that the `models` directory requires trained models to be put into it. These are generated from text files using [`train.py`](/train.py).

## Documentation on the Code

[Documentation for the code itself lives here](https://benshoeman.github.io/SonicOCBot/) and is automatically generated on push to `master`. It's generated using [pdoc](https://pdoc.dev/), which uses docstrings in the functions to create documentation. (This repo is documented using numpydoc format.)
