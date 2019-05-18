import random

import Directories
from SQLiteMarkovModel import SQLiteMarkovModel

class SonicSezGenerator:
    def __init__(self,
        text_database=f"{Directories.MODELS_DIR}/sonicsez.sqlite3"
    ):
        self.__text_model = SQLiteMarkovModel(text_database)

    def get_text(self):
        return "Sonic Sez: " + self.__text_model.get_random_paragraph(
            sentences=random.randint(1,3)
        )