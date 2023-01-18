import random
import re
import requests


class ProfanityFilter:
    """Filter that removes profanity from words, based on a newline-separated list.

    Parameters
    ----------
    censor_char : str
        character to censor using, by default "*"
    filter_list_url : str
        URL to pull profanity list from, by default "https://raw.githubusercontent.com/coffee-and-fun/google-profanity-words/main/data/list.txt"
    """

    _DEFAULT_FILTER_LIST = "https://raw.githubusercontent.com/coffee-and-fun/google-profanity-words/main/data/list.txt"

    def __init__(self, censor_pool: str = "!@#$%^*?", filter_list_url: str = _DEFAULT_FILTER_LIST) -> None:
        self.censor_pool = censor_pool if len(censor_pool) > 0 else "*"
        self._censor_char_index = 0
        try:
            response = requests.get(filter_list_url)
            self.filter_list = [word.strip() for word in response.text.strip().split("\n") if len(word) > 0]
        except ConnectionError:
            print(f"Couldn't connect to {filter_list_url}, loading empty list")
            self.filter_list = []

    def _randomize_censor_pool(self) -> None:
        """Randomize the current censor pool."""
        if len(self.censor_pool) > 1:
            new_censor_pool = sorted(self.censor_pool[:-1], key=lambda c: random.random())
            self.censor_pool = self.censor_pool[-1] + "".join(new_censor_pool)
            self._censor_char_index = 1

    def _get_next_censor_char(self) -> str:
        """Get the next character to censor with.

        Returns
        -------
        str
            next censor character
        """
        next_censor_char = self.censor_pool[self._censor_char_index]
        self._censor_char_index = (self._censor_char_index + 1) % len(self.censor_pool)
        # Shuffle censor pool when going back to 0
        if self._censor_char_index == 0:
            self._randomize_censor_pool()
        return next_censor_char

    def censor(self, string: str) -> str:
        """Censor all words that occur in the filter list from the string.

        Parameters
        ----------
        string : str
            string to be censored

        Returns
        -------
        str
            censored string
        """
        curr_string = string
        for word in self.filter_list:
            curr_string = re.sub("\\b" + re.escape(word) + "\\b", "".join(self._get_next_censor_char() for _ in range(len(word))), curr_string)
        return curr_string
