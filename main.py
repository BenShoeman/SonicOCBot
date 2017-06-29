#!/usr/bin/env python
# -*- coding: utf-8 -*-

import facebook
import io
import datetime
import os
import pytumblr
import re
import requests
import time
from PIL import Image, ImageDraw
from oc import *
from fanfic import *
from followerpost import *
import markov

FACEBOOK_CREDS = {
    "page_id": "678135995705395",
    "access_token": open("keys/fb.txt").read()
}
TUMBLR_CREDS = dict([re.split(r": ", e.strip()) for e in open("keys/tumblr.txt").readlines()])

# Facebook:
# Get the page ID by going onto the page > about; it'll be at the bottom of the page
# Get access token by going on developer.facebook.com > tools and support > Graph API Explorer > Get token
# Make sure to extend access token in this menu!

# Tumblr:
# Get oauth token and secret using api.tumblr.com/console

LIKE_MILESTONES = [int(x) for x in open("data/likemilestones.txt")]
FOLLOWER_MILESTONES = [int(x) for x in open("data/followermilestones.txt")]

def main():
    fbgraph = getGraph(FACEBOOK_CREDS)
    tumbclient = pytumblr.TumblrRestClient(
        TUMBLR_CREDS["consumer_key"], TUMBLR_CREDS["consumer_secret"],
        TUMBLR_CREDS["oauth_token"], TUMBLR_CREDS["oauth_secret"]
    )

    print "Sonic OC Bot started."

    # Start the bot process on the start of the minute
    time.sleep(0 if datetime.datetime.now().second == 0 else 60 - datetime.datetime.now().second)

    while True:
        # If we're on the hour or half-hour
        currtime = datetime.datetime.now()
        if currtime.minute % 30 == 0:
            try:
                # Get like and follower counts on FB and Tumblr
                likes = fbgraph.get_object(FACEBOOK_CREDS["page_id"], fields="fan_count")["fan_count"]
                followers = tumbclient.followers("sonicocbot")["total_users"]

                # If we have reached a milestone, post about it
                if likes >= LIKE_MILESTONES[0] or followers >= FOLLOWER_MILESTONES[0]:
                    if likes >= LIKE_MILESTONES[0]:
                        print "Posting like milestone:",LIKE_MILESTONES[0],"likes! ...",
                        likes = LIKE_MILESTONES[0]
                        del LIKE_MILESTONES[0]
                        # Update the new milestones
                        with open("data/likemilestones.txt","w") as f:
                            f.write("\n".join([str(x) for x in LIKE_MILESTONES]))

                        likeimg = getFollowerThanksImg(likes, "likes")

                        # Get jpeg of image in memory, then post that image to FB
                        output = io.BytesIO()
                        likeimg.save(output, format="PNG")
                        fbgraph.put_photo(message="We've reached %d likes on Facebook! Thanks for the support; we'll defeat Eggman in no time!" % likes, image=output.getvalue())
                        likeimg.save("temp.png", format="PNG")
                        resp = tumbclient.create_photo("sonicocbot", state="published", data=os.getcwd()+"/temp.png", caption="We've reached %d likes on Facebook! Thanks for the support; we'll defeat Eggman in no time!" % likes, tags=["thanks"])
                        os.remove("temp.png")

                        print "Done!"
                    if followers >= FOLLOWER_MILESTONES[0]:
                        print "Posting follower milestone:",LIKE_MILESTONES[0],"followers! ...",
                        followers = FOLLOWER_MILESTONES[0]
                        del FOLLOWER_MILESTONES[0]
                        # Update the new milestones
                        with open("data/followermilestones.txt","w") as f:
                            f.write("\n".join([str(x) for x in FOLLOWER_MILESTONES]))

                        followerimg = getFollowerThanksImg(followers, "followers")

                        # Get jpeg of image in memory, then post that image to FB
                        output = io.BytesIO()
                        followerimg.save(output, format="PNG")
                        fbgraph.put_photo(message="We've reached %d followers on Tumblr! Thanks for the support; now who's down for some chili dogs?" % followers, image=output.getvalue())
                        followerimg.save("temp.png", format="PNG")
                        resp = tumbclient.create_photo("sonicocbot", state="published", data=os.getcwd()+"/temp.png", caption="We've reached %d followers on Tumblr! Thanks for the support; now who's down for some chili dogs?" % followers, tags=["thanks"])
                        os.remove("temp.png")

                        print "Done!"
                # Post Sonic fanfic at midnight and noon on Tuesdays, Fridays,
                # and Saturdays
                elif currtime.weekday() in [1,4,5] and currtime.hour in [0,12] and currtime.minute == 0:
                    ffic = getRandomFanfic()
                    print "Posting fanfic", ffic["title"], "to FB page...",
                    fbgraph.put_wall_post(message=ffic["title"] + "\n\n-----\n\n" + ffic["content"])
                    print "Done!"

                    ffic = getRandomFanfic()
                    print "Posting fanfic", ffic["title"], "to Tumblr blog...",
                    resp = tumbclient.create_text("sonicocbot", state="published", title=ffic["title"], body=ffic["content"], tags=["sonic", "sanic", "sonic the hedgehog", "sonic fanfic", "sonic fanfiction", "fic", "fiction", "fanfic", "fanfiction", "sega", "bot"])
                    if "errors" in resp: print "Error."
                    else: print "Done!"
                # Post Sonic Sez at 6am, noon, and 6pm every day except on fanfic times
                elif currtime.hour in [6,12,18] and currtime.minute == 0:
                    advice = u"Sonic S̶e̶z̶ Says: " + markov.getRandomParagraph("text/sonicsez.sqlite3", sentences=gaussInt(4,2,minval=2))
                    print "Posting Sonic Sez to FB page...",
                    fbgraph.put_wall_post(message=advice)
                    print "Done!"

                    advice = markov.getRandomParagraph("text/sonicsez.sqlite3", sentences=gaussInt(4,2,minval=2))
                    print "Posting Sonic Sez to Tumblr blog...",
                    resp = tumbclient.create_text("sonicocbot", state="published", title="Sonic Sez", body=advice, tags=["sonic", "sanic", "sonic the hedgehog", "sonic sez", "sonic says", "sega", "bot"])
                    if "errors" in resp: print "Error."
                    else: print "Done!"
                # Otherwise just post an OC
                else:
                    oc = createOCFromTemplate()
                    print "Posting OC", oc["name"], "to FB page...",
                    # Get jpeg of image in memory, then post that image and OC desc. to FB
                    output = io.BytesIO()
                    oc["image"].save(output, format="PNG")
                    fbgraph.put_photo(message=getOCDescription(oc), image=output.getvalue())
                    print "Done!"

                    oc = createOCFromTemplate()
                    print "Posting OC", oc["name"], "to Tumblr blog...",
                    oc["image"].save("temp.png", format="PNG")
                    resp = tumbclient.create_photo("sonicocbot", format="markdown", state="published", data=os.getcwd()+"/temp.png", caption="## "+re.sub(r"(\S)\n(\S)","\\1<br/>\n\\2",getOCDescription(oc)), tags=["sonic", "sanic", "sonic the hedgehog", "fanart", "fan art", "sonic fanart", "sonic fan art", "oc", "sonic oc", "sonic fan character", "illustration", "drawing", "design", "sonic character design", "sega", oc["species"], oc["sex"], "bot", "lol"])
                    os.remove("temp.png")
                    if "errors" in resp: print "Error."
                    else: print "Done!"
            except (facebook.GraphAPIError, requests.exceptions.ConnectionError) as e:
                print "Error:",e.message

        time.sleep(60 - datetime.datetime.now().second)

    # Debug
    # oc = createOCFromTemplate()
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
