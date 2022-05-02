import os
import sys

PROJECT_DIR = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
"""Project's base directory derived from current file's path"""

DATA_DIR = os.path.join(PROJECT_DIR, "data")
"""Path for text data not associated with models (e.g. name list, animal list, fill info)"""

CREDENTIALS_DIR = os.path.join(PROJECT_DIR, "keys")
"""Path for keys/tokens needed for social media authentication"""

IMAGES_DIR = os.path.join(PROJECT_DIR, "images")
"""Path for Sonic Maker images"""

MODELS_DIR = os.path.join(PROJECT_DIR, "models")
"""Path for text generating models (as of now, only Markov models)"""

FONTS_DIR = os.path.join(PROJECT_DIR, "fonts")
"""Path for bitmap fonts used in OC creation"""

SONICMAKER_DIR = os.path.join(PROJECT_DIR, "sonicmaker")
"""Path for Sonic Maker creation data, including images and fill info"""

TEMPLATES_DIR = os.path.join(PROJECT_DIR, "templates")
"""Path for templates (including fill info)"""
