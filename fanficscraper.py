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

def main():
    choice = raw_input("Titles (t) or Fanfics (f)? ")
    if choice == "t":
        getTitles()
    else:
        getFanfics()

def getTitles():
    titlesTxt = ""

    signal.signal(signal.SIGALRM, timeoutHandler)

    # Spoof browser user agent just in case
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]

    # Set timeout to 5
    socket.setdefaulttimeout(5)

    for i in range(1,1171):
        url = "https://www.fanfiction.net/game/Sonic-the-Hedgehog/?&p=" + str(i)
        try:
            print "Getting titles of fanfics on",url

            # Wrapping in sigalrm in case of taking too long to load
            signal.alarm(5)
            content = opener.open(url).read()
            signal.alarm(0)

            soup = BeautifulSoup(content)
            for tag in soup.findAll("a", class_="stitle"):
                titlesTxt += unidecode(tag.get_text()) + ". "
            time.sleep(1)
        except httplib.BadStatusLine:
            print "Bad status line on",url
        except Exception as e:
            print e.message

    with open("fanfics.titles.txt","w") as f:
        f.write(titlesTxt)

# Write fanfics text to text file, but only do the first chapters of each so we
# don't take too much and so that we don't make the file waaay too large.
def getFanfics():
    MAX_CHAR_COUNT = 134217728 # 128 MB max should be more than enough
    fanficsTxt = ""

    signal.signal(signal.SIGALRM, timeoutHandler)

    # Spoof browser user agent just in case
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]

    # Set timeout to 5
    socket.setdefaulttimeout(5)

    for i in range(1,1171):
        url = "https://www.fanfiction.net/game/Sonic-the-Hedgehog/?&p=" + str(i)
        try:
            print "Getting text of fanfics on",url

            # Wrapping in sigalrm in case of taking too long to load
            signal.alarm(5)
            content = opener.open(url).read()
            signal.alarm(0)

            soup = BeautifulSoup(content)
            for tag in soup.findAll("a", class_="stitle"):
                try:
                    print "\tGetting text of fanfic at",tag.get("href")

                    # Go to that link
                    signal.alarm(5)
                    subcontent = opener.open("https://www.fanfiction.net"+tag.get("href")).read()
                    signal.alarm(0)
                    subsoup = BeautifulSoup(subcontent)

                    # If rated M, don't use this because we don't wanna get zucced
                    if "Fiction M" in subsoup.get_text():
                        continue

                    # Get the div with ID storytext and get all paragraphs within it
                    for p in subsoup.findAll(id="storytext")[0].findAll("p"):
                        p_text = profanity.censor(unidecode(p.get_text()))
                        # Add period if we don't have any at end of paragraph, so
                        # we don't break Markov chain
                        if not re.search(r"[.!?]$", p_text):
                            p_text += "."
                        fanficsTxt += p_text + " "

                    # If we've exceeded the char loop, exit the loop
                    if len(fanficsTxt) > MAX_CHAR_COUNT:
                        break

                    time.sleep(1)

                except httplib.BadStatusLine:
                    print "Bad status line"
                except Exception as e:
                    print e.message

            # If we've exceeded the char limit, exit the loop
            if len(fanficsTxt) > MAX_CHAR_COUNT:
                break

            time.sleep(1)
        except httplib.BadStatusLine:
            print "Bad status line on",url
        except Exception as e:
            print e.message

    with open("fanfics.txt","w") as f:
        f.write(fanficsTxt)

def timeoutHandler(signum, frame):
    raise Exception("Took too long to load page")

if __name__=="__main__":
    main()
