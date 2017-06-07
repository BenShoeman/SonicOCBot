#!/usr/bin/env python

import facebook
import io
import datetime
import time
from PIL import Image, ImageDraw
from oc import *
import markov

FACEBOOK_PAGE_ID = "678135995705395"
FACEBOOK_ACCESS_TOKEN = ""

# Get the page ID by going onto the page > about; it'll be at the bottom of the page
# Get access token by going on developer.facebook.com > tools and support > Graph API Explorer > Get token
# Make sure to extend access token in this menu!

def main():
    credentials = {
        "page_id": FACEBOOK_PAGE_ID,
        "access_token": FACEBOOK_ACCESS_TOKEN
    }
    graph = getGraph(credentials)

    print "Sonic OC Bot starting..."

    # Start the bot process on the start of the minute
    time.sleep(0 if datetime.datetime.now().second == 0 else 60 - datetime.datetime.now().second)

    while True:
        # If we're on the hour or half-hour
        if datetime.datetime.now().minute % 30 == 0:
            try:
                # Post Sonic Sez at noon every day
                if datetime.datetime.now().hour == 12 and datetime.datetime.now().minute == 0:
                    print "Posting Sonic Sez to FB page..."

                    advice = "Sonic S̶e̶z̶ Says: " + markov.getRandomParagraph("sonicsez.sqlite3")
                    graph.put_wall_post(message=advice)

                    print "Done!"
                # Most times just post an OC
                else:
                    oc = createOC()

                    # For debug
                    # oc["image"].show()
                    # print getOCDescription(oc)

                    print "Posting OC", oc["name"], "to FB page...",

                    # Get jpeg of image in memory, then post that image and OC desc. to FB
                    output = io.BytesIO()
                    oc["image"].save(output, format="PNG")
                    graph.put_photo(message=getOCDescription(oc), image=output.getvalue())

                    print "Done!"
            except (ConnectionError, facebook.GraphAPIError) as e:
                print "Error:",e.message

        time.sleep(60)

    # Debug
    # oc = createOC()
    # print getOCDescription(oc)
    # oc["image"].show()

# Graph API Examples:
# timepost = time.strftime("It is %H:%M %Z on %B %d, %Y.", time.localtime())
# graph.put_wall_post(message=timepost)
#
# img = open("Coldsteel.png", "rb")
# graph.put_photo(message="pssssh... nothin personnel... kid...", image=img)

def getGraph(creds):
    graph = facebook.GraphAPI(creds["access_token"])
    response = graph.get_object("me/accounts")
    page_access_token = None

    for page in response["data"]:
        if page["id"] == creds["page_id"]:
            page_access_token = page["access_token"]

    if page_access_token:
        graph = facebook.GraphAPI(page_access_token)
    else:
        raise Exception("Error getting page access token; possibly wrong page ID?")

    return graph

if __name__=="__main__":
    main()
