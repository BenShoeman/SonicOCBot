#!/usr/bin/env python

import random
import re
import sqlite3
import sys

extrapunctregex = re.compile(r"[\/#$%\^\*{}=_`~()\"]")
wordregex = re.compile(r"([A-Za-z0-9\-\']+|[.,!?&;:])")

def makeTable(sqldb):
    con = sqlite3.connect(sqldb)
    try:
        cur = con.cursor()

        # Determine if SQL table exists
        cur.execute("select name from sqlite_master where type='table' and name='markov_edges';")
        # ...and then add if it doesn't
        if len(cur.fetchall()) == 0:
            cur.execute("create table markov_edges (currword varchar, nextword varchar, instances int, probability real);")
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

    words = wordregex.findall(text)

    con = sqlite3.connect(sqldb)

    try:
        cur = con.cursor()

        for i in range(len(words) - 1):
            currword = words[i]
            nextword = words[i+1]

            # Escape single quotes properly
            currword = currword.replace("'","''")
            nextword = nextword.replace("'","''")

            # Try to find this edge
            cur.execute("select * from markov_edges where currword='%s' and nextword='%s';" % (currword, nextword))

            # If edge doesn't exist, add it
            if len(cur.fetchall()) == 0:
                # print "Adding edge currword=%s, nextword=%s" % (currword, nextword)
                cur.execute("insert into markov_edges (currword, nextword, instances, probability) values ('%s', '%s', 1, 0.0);" % (currword, nextword))
            # Otherwise increment number of instances
            else:
                # print "Updating edge currword=%s, nextword=%s" % (currword, nextword)
                cur.execute("update markov_edges set instances = instances + 1 where currword='%s' and nextword='%s';" % (currword, nextword))

            # Calculate new probabilities

            # print "Getting total instances of currword=%s" % currword
            cur.execute("select sum(instances) from markov_edges where currword='%s';" % currword)
            totalinstances = cur.fetchall()[0][0]

            # print "Getting all edges with currword=%s" % currword
            cur.execute("select * from markov_edges where currword='%s';" % currword)
            for r in cur.fetchall():
                currinstances = r[2]
                nextword = r[1].replace("'","''")
                currprob = float(currinstances) / float(totalinstances)
                # print "Updating probability of currword=%s" % currword
                cur.execute("update markov_edges set probability = %f where currword='%s' and nextword='%s';" % (currprob, currword, nextword))

        con.commit()
    except sqlite3.OperationalError as e:
        print "Error:", e.message
        con.rollback()
    finally:
        con.close()

def getRandomString(sqldb):
    con = sqlite3.connect(sqldb)

    try:
        cur = con.cursor()

        # Pick random word in words
        currword = "."
        while re.search(r"[.,!?;:]", currword): # Make sure it's not a punctuation mark
            cur.execute("select distinct nextword from markov_edges where currword='.';")
            currword = random.choice(cur.fetchall())[0]

        currstring = currword[0:1].upper() + currword[1:]

        while currword != ".":
            # Get all possible next words
            cur.execute("select nextword, probability from markov_edges where currword='%s';" % currword.replace("'","''"))

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
            if len(currstring.split(" ")) < 30 and currword == ".":
                while re.search(r"[.,!?;:]", currword): # Make sure it's not a punctuation mark
                    cur.execute("select distinct nextword from markov_edges where currword='.';")
                    currword = random.choice(cur.fetchall())[0]
                currstring += " " + currword

    except sqlite3.OperationalError as e:
        print "Error:", e.message
        currstring = None
        con.rollback()
    finally:
        con.close()
        return currstring

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
    if len(sys.argv) == 3:
        if sys.argv[2] == "delete":
            deleteTable(sys.argv[1])
        elif sys.argv[2] == "get":
            print getRandomString(sys.argv[1])
        else:
            makeTable(sys.argv[1])
            with open(sys.argv[2]) as f:
                for l in f.readlines():
                    addText(sys.argv[1], l.replace("\r\n"," ").replace("\n"," "))
    else:
        print "Usage: %s <sqlite3 file> <text file>: add text file to markov chain\n       %s <sqlite3 file> delete: delete markov db\n       %s <sqlite3 file> get: get random string" % (sys.argv[0], sys.argv[0], sys.argv[0])
