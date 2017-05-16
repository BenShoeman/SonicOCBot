#!/usr/bin/env python

import facebook
import io
import json
import random
import datetime
import time
from PIL import Image, ImageDraw
from colors import *

FACEBOOK_PAGE_ID = "678135995705395"
FACEBOOK_ACCESS_TOKEN = "add access token here"

FILLINFO = json.loads(open("templates/fillinfo.json").read())

NAMES_FEMALE = open("names_female.txt").readlines()
NAMES_MALE = open("names_male.txt").readlines()
PERSONALITIES = open("personalities.txt").readlines()
SKILLS = open("skills.txt").readlines()

GENERAL_COLORS = getColorsList("generalcolors.txt")
SKIN_TONES = getColorsList("skintones.txt")

# Remove newlines read in with readlines
NAMES_FEMALE = [x.replace("\n","") for x in NAMES_FEMALE]
NAMES_MALE = [x.replace("\n","") for x in NAMES_MALE]
PERSONALITIES = [x.replace("\n","") for x in PERSONALITIES]
SKILLS = [x.replace("\n","") for x in SKILLS]

# Get the page ID by going onto the page > about; it'll be at the bottom of the page
# Get access token by going on developer.facebook.com > tools and support > Graph API Explorer > Get token
# Make sure to extend access token in this menu!

def main():
    credentials = {
        "page_id": FACEBOOK_PAGE_ID,
        "access_token": FACEBOOK_ACCESS_TOKEN
    }
    graph = getGraph(credentials)

    while True:
        # If we're on the hour or half-hour
        if datetime.datetime.now().minute % 30 == 0:
            oc = createOC()

            # For debug
            # oc["image"].show()
            # print getOCDescription(oc)

            print "Posting", oc["name"], "to FB page...",

            # Get jpeg of image in memory, then post that image and OC desc. to FB
            output = io.BytesIO()
            oc["image"].save(output, format="PNG")
            graph.put_photo(message=getOCDescription(oc), image=output.getvalue())

            print "Done!"

        time.sleep(60)

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

def createOC(templatenum = -1): # templatenum is for debug purposes
    oc = {}

    if templatenum < 0:
        # Picking a random template to use
        template = random.choice(FILLINFO["templates"])
    else:
        template = FILLINFO["templates"][templatenum]

    oc["image"] = Image.open("templates/" + template["image"]).convert("RGB")
    oc["gender"] = template["gender"]
    oc["species"] = template["species"]
    oc["age"] = max([int(round(random.gauss(21, 6))), 13])

    # Give it a name
    if oc["gender"] == "female":
        oc["name"] = random.choice(NAMES_FEMALE)
    elif oc["gender"] == "male":
        oc["name"] = random.choice(NAMES_MALE)

    oc["personality"] = random.choice(PERSONALITIES)

    oc["skills"] = []
    skillsnum = int(max([1, random.gauss(3.5, 2)]))
    for i in range(skillsnum):
        newskill = random.choice(SKILLS)
        if newskill not in oc["skills"]:
            oc["skills"].append(newskill)

    # Filling in each region with random colors
    for reg in template["fill"]:
        if reg["region"] == "skin":
            regColor = random.choice(SKIN_TONES)
        else:
            regColor = random.choice(GENERAL_COLORS)
        oc[reg["region"]] = regColor["name"]
        clr = randomizeColor(regColor["color"])

        try:
            for coord in reg["coords"]:
                ImageDraw.floodfill(oc["image"], tuple(coord), clr)
        except:
            pass

        try:
            for coord in reg["coords-shade"]:
                ImageDraw.floodfill(oc["image"], tuple(coord), darkenColor(clr))
        except:
            pass

        try:
            for coord in reg["coords-tint"]:
                ImageDraw.floodfill(oc["image"], tuple(coord), brightenColor(clr))
        except:
            pass

        try:
            for coord in reg["coords-complement"]:
                ImageDraw.floodfill(oc["image"], tuple(coord), complementaryColor(clr))
        except:
            pass

        try:
            for coord in reg["coords-analogccw"]:
                ImageDraw.floodfill(oc["image"], tuple(coord), analogousCCWColor(clr))
        except:
            pass

        try:
            for coord in reg["coords-analogcw"]:
                ImageDraw.floodfill(oc["image"], tuple(coord), analogousCWColor(clr))
        except:
            pass

    return oc

def getOCDescription(oc):
    oc_desc = oc["name"] + " the " + oc["species"].title() + "\n\n"
    # oc_desc += "Name: " + oc["name"] + "\n"
    # oc_desc += "Species: " + oc["species"].title() + "\n"
    oc_desc += "Age: " + str(oc["age"]) + "\n"
    oc_desc += "Sex: " + oc["gender"].title() + "\n"
    oc_desc += "Personality: " + oc["personality"].title() + "\n"
    oc_desc += "Skills/Passions: " + ", ".join(oc["skills"]).title() + "\n"
    for k,v in sorted(oc.iteritems()):
        if k not in ["name", "gender", "image", "species", "age", "personality", "skills"]:
            oc_desc += k.title() + " Color: " + v.title() + "\n"
    return oc_desc[0:-1]

if __name__=="__main__":
    main()
