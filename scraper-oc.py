#!/usr/bin/env python

from bs4 import BeautifulSoup
from unidecode import unidecode
import httplib
from profanity import profanity; profanity.set_censor_characters("*")
import re
import signal
import socket
import time
import urllib2

# Suppress pointless (for my purposes) bs4 warning
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

def main():
    getOCDescs()

def getOCDescs():
    femOCTxt = ""
    malOCTxt = ""

    removal_regex = re.compile(r"([.,!?]|\(.*?\)| \".*?\"(?: |$)|[aA][kK][aA].*| [Tt]he .*|Elder Identity|Elder\. Identity|\")")

    signal.signal(signal.SIGALRM, timeoutHandler)

    # Spoof browser user agent just in case
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]

    # Set timeout to 5
    socket.setdefaulttimeout(5)

    # First getting individual characters
    for i in range(1,6):
        url = "http://sonicfanchara.wikia.com/wiki/Category:Characters?page=" + str(i)
        try:
            print "Getting descriptions of OCs on",url

            # Wrapping in sigalrm in case of taking too long to load
            signal.alarm(5)
            content = opener.open(url).read()
            signal.alarm(0)

            soup = BeautifulSoup(content)
            for tag in soup.findAll(id="mw-pages")[0].findAll("div", class_="category-gallery-item"):
                try:
                    link = tag.findAll("a")[0]

                    signal.alarm(5)
                    subcontent = opener.open(link.get("href")).read()
                    signal.alarm(0)
                    subsoup = BeautifulSoup(subcontent)

                    # First get OC's name in title
                    ocname = subsoup.findAll("div", class_="header-column header-title")[0].findAll("h1")[0].get_text()
                    # ...and remove unnecessary stuff
                    ocname = removal_regex.sub("", ocname).strip()

                    if "Character" in ocname: # for some reason they have a self-reference?
                        continue
                    else:
                        print "\tGetting description of " + ocname + "..."

                    # We want name references to be removed so make a regex to remove the refs
                    ocname_tosubjectivebeg_regex = re.compile(r"(^|[\.!?] )(" + "|".join(ocname.split(" "))
                        + ("|" + ocname if len(ocname.split(" ")) > 1 else "") + ")")
                    ocname_tosubjectivemid_regex = re.compile(r"(^|[,:;] )(" + "|".join(ocname.split(" "))
                        + ("|" + ocname if len(ocname.split(" ")) > 1 else "") + ")")
                    ocname_toobjective_regex = re.compile(r"(\w )(" + "|".join(ocname.split(" "))
                        + ("|" + ocname if len(ocname.split(" ")) > 1 else "") + ")")
                    ocname_topossesivebeg_regex = re.compile(r"(^|[\.!?] )(" + "|".join(ocname.split(" "))
                        + ("|" + ocname if len(ocname.split(" ")) > 1 else "") + ")'s?")
                    ocname_topossesivemid_regex = re.compile(r"([\w,:;] )(" + "|".join(ocname.split(" "))
                        + ("|" + ocname if len(ocname.split(" ")) > 1 else "") + ")'s?")

                    octextsoup = subsoup.findAll("div", id="mw-content-text")[0]

                    # Determining if OC is male or female dependent upon how many
                    # references to he/his or she/her(s) there are.
                    # Efficient trick found at https://stackoverflow.com/questions/17268958/finding-occurrences-of-a-word-in-a-string-in-python-3
                    numMaleRefs = sum(1 for _ in re.finditer(r'\b([Hh]e|[Hh]is|[Hh]im)\b',octextsoup.get_text()))
                    numFemaleRefs = sum(1 for _ in re.finditer(r'\b([Ss]he|[Hh]ers?)\b',octextsoup.get_text()))
                    isMale = numMaleRefs > numFemaleRefs

                    for p in octextsoup.findAll("p"):
                        if len(p.get_text().split(" ")) > 10 and len(re.split(r"[\.!?] ",p.get_text())) > 2 and "Basic Stats" not in p.get_text() and \
                          not re.search(r"^(\w+( \w+){0,3}:|\d+\.|\-|\(|SS\s)",unidecode(p.get_text())):
                            ptext = unidecode(p.get_text().strip())
                            # Perform re substitutions based on gender and name
                            subpronoun = "he" if isMale else "she"
                            objpronoun = "him" if isMale else "her"
                            pospronoun = "his" if isMale else "her"
                            ptext = ocname_topossesivebeg_regex.sub(
                                r"\1" + pospronoun.title(), ptext
                            )
                            ptext = ocname_topossesivemid_regex.sub(
                                r"\1" + pospronoun, ptext
                            )
                            ptext = ocname_tosubjectivebeg_regex.sub(
                                r"\1" + subpronoun.title(), ptext
                            )
                            ptext = ocname_tosubjectivemid_regex.sub(
                                r"\1" + subpronoun, ptext
                            )
                            ptext = ocname_toobjective_regex.sub(
                                r"\1" + objpronoun, ptext
                            )
                            inserttext = profanity.censor(ptext)

                            # Add period if we don't have any at end of paragraph, so
                            # we don't break Markov chain
                            if not re.search(r"[.!?]$", ptext):
                                ptext += "."
                            if isMale:
                                malOCTxt += ptext + " "
                            else:
                                femOCTxt += ptext + " "

                    time.sleep(1)

                except httplib.BadStatusLine:
                    print "Bad status line"
                except Exception as e:
                    print e.message

            time.sleep(1)
        except httplib.BadStatusLine:
            print "Bad status line on",url
        except Exception as e:
            print e.message

    with open("text/malocdescs.txt","w") as f:
        f.write(malOCTxt)
    with open("text/femocdescs.txt","w") as f:
        f.write(femOCTxt)

def timeoutHandler(signum, frame):
    raise Exception("Took too long to load page")

if __name__=="__main__":
    main()