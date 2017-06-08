#!/usr/bin/env python

import random
import re
import sqlite3
import sys

extrapunctregex = re.compile(r"[\/#$%\^{}=_`~()\"]")
wordregex = re.compile(r"([A-Za-z0-9\-\']+|[.,!?&;:])")

def makeTable(sqldb):
    con = sqlite3.connect(sqldb)
    try:
        cur = con.cursor()

        # Determine if SQL table exists
        cur.execute("select name from sqlite_master where type='table' and name='markov_edges';")
        # ...and then add if it doesn't
        if len(cur.fetchall()) == 0:
            cur.execute("create table markov_edges (currword varchar, nextword varchar, instances int);")
            con.commit()
    except sqlite3.OperationalError as e:
        print "Error:", e.message
        con.rollback()
    finally:
        con.close()

def addText(sqldb, text):
    # Remove unnecessary punctuation
    text = extrapunctregex.sub("", text)
    if text == "":
        return
    text = ". " + text

    words = wordregex.findall(text)

    con = sqlite3.connect(sqldb)

    try:
        cur = con.cursor()

        for i in range(len(words) - 1):
            currword = words[i]
            nextword = words[i+1]

            print currword,

            # Escape single quotes properly
            currword = currword.replace("'","''")
            nextword = nextword.replace("'","''")

            # Try to find this edge
            cur.execute("select * from markov_edges where currword='%s' and nextword='%s';" % (currword, nextword))

            # If edge doesn't exist, add it
            if len(cur.fetchall()) == 0:
                # print "Adding edge currword=%s, nextword=%s" % (currword, nextword)
                cur.execute("insert into markov_edges (currword, nextword, instances) values ('%s', '%s', 1);" % (currword, nextword))
            # Otherwise increment number of instances
            else:
                # print "Updating edge currword=%s, nextword=%s" % (currword, nextword)
                cur.execute("update markov_edges set instances = instances + 1 where currword='%s' and nextword='%s';" % (currword, nextword))

            if i % 5000 == 4999: con.commit() # Commit every 5000 words

            # Unnecessary, was slowing the program down when we can calculate
            # probabilities in the select query in getRandomString

            # # Calculate new probabilities
            #
            # # print "Getting total instances of currword=%s" % currword
            # cur.execute("select sum(instances) from markov_edges where currword='%s';" % currword)
            # totalinstances = cur.fetchall()[0][0]
            #
            # # print "Getting all edges with currword=%s" % currword
            # cur.execute("select * from markov_edges where currword='%s';" % currword)
            # for r in cur.fetchall():
            #     currinstances = r[2]
            #     nextword = r[1].replace("'","''")
            #     currprob = float(currinstances) / float(totalinstances)
            #     # print "Updating probability of currword=%s" % currword
            #     cur.execute("update markov_edges set probability = %f where currword='%s' and nextword='%s';" % (currprob, currword, nextword))

        con.commit()

    except sqlite3.OperationalError as e:
        print "Error:", e.message
        con.rollback()
    finally:
        con.close()

def getRandomString(sqldb, words = 30):
    con = sqlite3.connect(sqldb)

    try:
        cur = con.cursor()

        # Pick random word in words
        currword = "."
        while re.search(r"[.,!?;:]", currword): # Make sure it's not a punctuation mark
            cur.execute("select distinct nextword from markov_edges where currword='.' or currword='!' or currword='?';")
            currword = random.choice(cur.fetchall())[0]

        currstring = currword

        while not re.search(r"[.!?]", currword):
            # Get all possible next words
            cur.execute("select nextword, cast(instances as float) / (select sum(instances) from markov_edges where currword='%s') as probability from markov_edges where currword='%s';" % (currword.replace("'","''"), currword.replace("'","''")))

            # Get next word using probability
            n = random.uniform(0,1)
            rows = cur.fetchall()
            if len(rows) > 0:
                for r in rows:
                    currword = r[0]; prob = r[1]
                    if n < prob:
                        break
                    n -= prob
            else:
                # Select new random word since we don't have one
                cur.execute("select distinct currword from markov_edges;")
                currword = random.choice(cur.fetchall())[0]

            if not re.search(r"[.,!?;:]", currword):
                currstring += " "

            # Add next word to string
            currstring += currword

            # Add another sentence if the description is really short
            if len(currstring.split(" ")) == words:
                break

    except sqlite3.OperationalError as e:
        print "Error:", e.message
        currstring = None
        con.rollback()
    finally:
        con.close()
        return currstring

def getRandomStringMin(sqldb, wordmin = 30):
    con = sqlite3.connect(sqldb)

    try:
        cur = con.cursor()

        # Pick random word in words
        currword = "."
        while re.search(r"[.,!?;:]", currword): # Make sure it's not a punctuation mark
            cur.execute("select distinct nextword from markov_edges where currword='.' or currword='!' or currword='?';")
            currword = random.choice(cur.fetchall())[0]

        currstring = currword

        while not re.search(r"[.!?]", currword):
            # Get all possible next words
            cur.execute("select nextword, cast(instances as float) / (select sum(instances) from markov_edges where currword='%s') as probability from markov_edges where currword='%s';" % (currword.replace("'","''"), currword.replace("'","''")))

            # Get next word using probability
            n = random.uniform(0,1)
            rows = cur.fetchall()
            if len(rows) > 0:
                for r in rows:
                    currword = r[0]; prob = r[1]
                    if n < prob:
                        break
                    n -= prob
            else:
                # Select new random word since we don't have one
                cur.execute("select distinct currword from markov_edges;")
                currword = random.choice(cur.fetchall())[0]

            if not re.search(r"[.,!?;:]", currword):
                currstring += " "

            # Add next word to string
            currstring += currword

            # Add another sentence if the description is really short
            if len(currstring.split(" ")) < wordmin and re.search(r"[.!?]", currword):
                while re.search(r"[.,!?;:]", currword): # Make sure it's not a punctuation mark
                    cur.execute("select distinct nextword from markov_edges where currword='.' or currword='!' or currword='?';")
                    currword = random.choice(cur.fetchall())[0]
                currstring += " " + currword

    except sqlite3.OperationalError as e:
        print "Error:", e.message
        currstring = None
        con.rollback()
    finally:
        con.close()
        return currstring

def getRandomSentence(sqldb):
    sentence = getRandomStringMin(sqldb, wordmin = 1)
    sentence = sentence[0:1].upper() + sentence[1:]
    return sentence

def getRandomParagraph(sqldb, sentences = 5):
    # Generates sentences sentences, puts them in a list, and then joins them with spaces.
    return " ".join([getRandomSentence(sqldb) for i in range(sentences)])

def deleteTable(sqldb):
    con = sqlite3.connect(sqldb)
    try:
        cur = con.cursor()

        # Determine if SQL table exists
        cur.execute("select name from sqlite_master where type='table' and name='markov_edges';")
        # ...and then delete if it does
        if len(cur.fetchall()) > 0:
            cur.execute("drop table markov_edges;")
            con.commit()
    except sqlite3.OperationalError as e:
        print "Error:", e.message
        con.rollback()
    finally:
        con.close()

if __name__=="__main__":
    if len(sys.argv) == 3 and sys.argv[2] == "delete":
        deleteTable(sys.argv[1])
    elif len(sys.argv) == 4 and sys.argv[2] == "get":
        if sys.argv[3] == "p":
            print getRandomParagraph(sys.argv[1])
        elif sys.argv[3] == "s":
            print getRandomSentence(sys.argv[1])
    elif len(sys.argv) == 3:
        makeTable(sys.argv[1])
        with open(sys.argv[2]) as f:
            for l in f.readlines():
                addText(sys.argv[1], l.replace("\r\n"," ").replace("\n"," "))
    else:
        print "Usage: %s <sqlite3 file> <text file>: add text file to markov chain\n       %s <sqlite3 file> delete: delete markov db\n       %s <sqlite3 file> get s/p: get random sentence/paragraph" % (sys.argv[0], sys.argv[0], sys.argv[0])
