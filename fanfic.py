import random
from markov import *

def getRandomFanfic():
    fanfic = {}

    fanfic["title"] = getRandomSentence("fanfics.titles.sqlite3")
    # If last character is period, remove it since those were just added to
    # separate titles
    if fanfic["title"][-1] == ".": fanfic["title"] = fanfic["title"][0:-1]

    fanfic["content"] = "\n\n".join([getRandomParagraph("fanfics.sqlite3") for i in range(100)])

    return fanfic
