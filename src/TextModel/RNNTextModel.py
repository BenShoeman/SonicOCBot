import json
import numpy as np
from numpy.typing import ArrayLike
import os
import random
import tensorflow.keras as keras
from tensorflow.keras import models
from typing import Optional

import src.Directories as Directories
from src.TextModel.TextModel import TextModel


class RNNTextModel(TextModel):
    """Text model that uses a RNN to generate text. This is based off the RNNs generated from the `models/training.ipynb` notebook.

    Parameters
    ----------
    model_name : str
        name of the model, which requires files `models/{model_name}.model.h5` and `models/{model_name}.wordmap.json`
    predict_temperature : float
        temperature of the next word prediction, where a higher temperature will get more random results
    sequence_length : int
        length of the input sequences to the model, defined in the training notebook
    seed : Optional[list]
        optional seed to provide the model for text generation; if not provided, this is randomly generated
    """

    def __init__(self, model_name: str, predict_temperature: float = 0.45, sequence_length: int = 20, seed: Optional[list] = None):
        self.__sequence_length = sequence_length  # Defined in the training notebook, make sure these match
        self.__temperature = predict_temperature
        self.__model = models.load_model(os.path.join(Directories.MODELS_DIR, f"{model_name}.model.h5"))
        with open(os.path.join(Directories.MODELS_DIR, f"{model_name}.wordmap.json")) as f:
            # Fix JSON requiring keys to be strings by making them ints again
            self.__idx_word = {int(key): val for key, val in json.load(f).items()}
            self.__max_word_idx = max(key for key in self.__idx_word.keys())
        self.__initialize_pattern_seed(seed)

    def __initialize_pattern_seed(self, seed: Optional[list] = None) -> None:
        """Initialize the seed of the RNN.

        Parameters
        ----------
        seed : Optional[list]
            manually provided seed if a random one is not desired, by default None
        """
        if seed is not None:
            self.__pattern = seed
        else:
            self.__pattern = [random.randint(1, self.__max_word_idx) for _ in range(self.__sequence_length - 1)]
            # Run the pattern through the whole sequence to forget the random sequence
            for _ in range(self.__sequence_length):
                self.get_next_word()

    def __sample(self, prediction: ArrayLike) -> np.intp:
        """Based on an array of probabilities for each index, randomly pick an index.

        Parameters
        ----------
        prediction : ArrayLike
            prediction from the RNN

        Returns
        -------
        np.intp
            index of the word chosen (which will be converted to a word from the wordmap `__idx_word`)
        """
        prediction_arr = np.asarray(prediction, dtype=np.float64)
        if self.__temperature > 0:
            prediction_arr = np.log(prediction_arr) / self.__temperature
            exp_prediction = np.exp(prediction_arr)
            prediction_arr = exp_prediction / np.sum(exp_prediction)
        probabilities = np.random.multinomial(1, np.asarray(prediction_arr[0, :], dtype=np.float64), 1)
        return np.argmax(probabilities)

    def get_next_word(self) -> str:
        """Use the RNN to get the next word.

        Returns
        -------
        str
            next word from the model
        """
        # Run prediction through the model and get the index of the prediction
        input_sequence = np.reshape(self.__pattern, (1, len(self.__pattern)))
        prediction = self.__model.predict(input_sequence, verbose=0)
        idx = self.__sample(prediction)

        # Adjust current pattern to include newly generated word
        self.__pattern.append(idx)
        self.__pattern = self.__pattern[1:]

        return self.__idx_word.get(int(idx), "")
