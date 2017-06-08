import random
from markov import *

MEAN_PARAS_PER_STORY = 61.906843
STDEV_PARAS_PER_STORY = 72.209921
MEAN_SENTS_PER_PARA = 4.279888
STDEV_SENTS_PER_PARA = 4.056850

def getRandomFanfic():
    fanfic = {}

    fanfic["title"] = getRandomSentence("text/fanfics.titles.sqlite3")
    # If last character is period, remove it since those were just added to
    # separate titles
    if fanfic["title"][-1] == ".": fanfic["title"] = fanfic["title"][0:-1]

    # For testing
    # fanfic["content"] = "\n\n".join([getRandomParagraph("text/fanfics.sqlite3") for i in range(10)])

    fanfic["content"] = ""
    for i in range(gaussInt(MEAN_PARAS_PER_STORY, STDEV_PARAS_PER_STORY, minval=1)):
        sentNum = gaussInt(MEAN_SENTS_PER_PARA, STDEV_SENTS_PER_PARA, minval=1)
        fanfic["content"] += getRandomParagraph("text/fanfics.sqlite3") + "\n\n"

    # Remove trailing newline chars
    fanfic["content"] = fanfic["content"][0:-2]

    return fanfic

def gaussInt(mean, stdev, minval = 0):
    return max([minval, int(round(random.gauss(mean,stdev)))])
