import os
import random

import Directories
from SQLiteMarkovModel import SQLiteMarkovModel

class FanfictionGenerator:
    __DEFAULT_KWARGS = {
        "mean_paragraphs": 40,
        "stdev_paragraphs": 30,
        "mean_sentences": 4.5,
        "stdev_sentences": 4
    }

    def gauss_int(mean, stdev, min_val=0):
        return max([min_val, round(random.gauss(mean,stdev))])

    def __init__(self,
        text_database=os.path.join(Directories.MODELS_DIR, "fanfics.sqlite3"),
        titles_database=os.path.join(Directories.MODELS_DIR, "fanfic-titles.sqlite3"),
        **kwargs
    ):
        self.__text_model = SQLiteMarkovModel(text_database)
        self.__titles_model = SQLiteMarkovModel(titles_database)
        self.__mean_paragraphs = kwargs.get(
            "mean_paragraphs", FanfictionGenerator.__DEFAULT_KWARGS["mean_paragraphs"]
        )
        self.__stdev_paragraphs = kwargs.get(
            "stdev_paragraphs", FanfictionGenerator.__DEFAULT_KWARGS["stdev_paragraphs"]
        )
        self.__mean_sentences = kwargs.get(
            "mean_sentences", FanfictionGenerator.__DEFAULT_KWARGS["mean_sentences"]
        )
        self.__stdev_sentences = kwargs.get(
            "stdev_sentences", FanfictionGenerator.__DEFAULT_KWARGS["stdev_sentences"]
        )

    # Returns a tuple of (title, text).
    def get_fanfiction(self):
        # Titles are regular sentences in the database, so remove the end
        # puncutation if it's a period
        title = self.__titles_model.get_random_sentence()
        if title[-1] == '.': title = title[:-1]
        text = ""
        for _ in range(FanfictionGenerator.gauss_int(
                self.__mean_paragraphs, self.__stdev_paragraphs, min_val=1
        )):
            n_sentences = FanfictionGenerator.gauss_int(
                self.__mean_sentences, self.__stdev_paragraphs, min_val=1
            )
            text += ("    " +
                self.__text_model.get_random_paragraph(sentences=n_sentences) +
                "\n")
        # Remove trailing newline
        text = text[:-1]

        return title, text

class TwitterFanfictionGenerator(FanfictionGenerator):
    def __init__(self):
        super().__init__(
            mean_paragraphs=3.25, stdev_paragraphs=0.75,
            mean_sentences=4.5, stdev_sentences=2
        )