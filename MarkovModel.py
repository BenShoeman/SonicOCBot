from abc import ABC, abstractmethod
import random
import re

EXTRA_PUNCTUATION_REGEX = re.compile(r"[\/#$%\^{}=_`~()\"]")
WORD_REGEX = re.compile(r"([A-Za-z0-9\-\']+|[.,!?&;:])")

class MarkovModel(ABC):
    # Create the Markov edge if it doesn't exist, or add 1 to the number of
    # instances of that edge if it does
    @abstractmethod
    def add_pair(self, current_word, next_word):
        pass

    def add_text(self, text):
        # Remove unnecessary punctuation
        text = EXTRA_PUNCTUATION_REGEX.sub("", text).strip()
        if text == "":
            return
        # Add period so we know the first word begins a sentence
        text = ". " + text
        
        words = WORD_REGEX.findall(text)
        for current_word, next_word in zip(words[:-1], words[1:]):
            self.add_pair(current_word, next_word)
    
    # get_random_word should return a single word, can be a punctuation mark if
    # include_punctuation is True. Should be first word of a sentence (a word
    # preceded by an end punctuation mark) if first_word is True.
    @abstractmethod
    def get_random_word(self, first_word=False, include_punctuation=False):
        pass
    
    # get_next_words should return a list of (word, probability) tuples, where
    # sum(probabilities) == 1.
    @abstractmethod
    def get_next_words(self, current_word):
        pass

    def get_random_sentence(self):
        current_word = self.get_random_word(first_word=True)
        sentence = current_word
        while current_word not in ['.', '!', '?']:
            next_word_probabilities = self.get_next_words(current_word)
            if len(next_word_probabilities) > 0:
                n = random.random()
                for word, pr_word in next_word_probabilities:
                    if n < pr_word:
                        current_word = word
                        break
                    n -= pr_word
            else:
                current_word = self.get_random_word(include_punctuation=True)
            
            # Add a space if current_word is not a punctuation mark
            if current_word not in ['.', ',', '!', '?', ';', ':']:
                sentence += ' '
            
            # Then add the word to the string
            sentence += current_word
        return sentence
    
    def get_random_paragraph(self, sentences=5):
        return ' '.join(self.get_random_sentence() for _ in range(sentences))