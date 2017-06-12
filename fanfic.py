#!/usr/bin/env python

import random
from markov import *

MEAN_PARAS_PER_STORY = 41.906843
STDEV_PARAS_PER_STORY = 37.209921
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
    for i in range(gaussInt(MEAN_PARAS_PER_STORY, STDEV_PARAS_PER_STORY, minval=4)):
        sentNum = gaussInt(MEAN_SENTS_PER_PARA, STDEV_SENTS_PER_PARA, minval=1)
        fanfic["content"] += getRandomParagraph("text/fanfics.sqlite3", sentences=sentNum) + "\n\n"

    # Remove trailing newline chars
    fanfic["content"] = fanfic["content"][0:-2]

    return fanfic

def gaussInt(mean, stdev, minval = 0):
    return max([minval, int(round(random.gauss(mean,stdev)))])

# Run in console to get a md file of the fanfic
def main():
    import re
    print "Generating fanfic...",
    ffic = getRandomFanfic()
    print "Done!"
    fname = re.sub(r"[\.,:;!?'\" ]","",ffic["title"]) + ".md"
    print "Writing fanfic to",fname,
    with open(fname,"w") as f:
        f.write("## " + ffic["title"] + "\n\n")
        f.write(ffic["content"])
    print "Done!"

if __name__=="__main__":
    main()
