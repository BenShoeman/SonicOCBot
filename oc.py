import json
import random
from PIL import Image, ImageDraw
from colors import *
from stats import *
import markov

FILLINFO = json.loads(open("templates/fillinfo.json").read())

NAMES_FEMALE = open("data/names_female.txt").readlines()
NAMES_MALE = open("data/names_male.txt").readlines()
PERSONALITIES = open("data/personalities.txt").readlines()
SKILLS = open("data/skills.txt").readlines()

GENERAL_COLORS = getColorsList("data/generalcolors.txt")
SKIN_TONES = getColorsList("data/skintones.txt")

# Remove newlines read in with readlines
NAMES_FEMALE = [x.replace("\n","") for x in NAMES_FEMALE]
NAMES_MALE = [x.replace("\n","") for x in NAMES_MALE]
PERSONALITIES = [x.replace("\n","") for x in PERSONALITIES]
SKILLS = [x.replace("\n","") for x in SKILLS]

def createOC(templatenum = -1): # templatenum is for debug purposes
    oc = {}

    if templatenum < 0:
        # Picking a random template to use
        template = random.choice(FILLINFO["templates"])
    else:
        template = FILLINFO["templates"][templatenum]

    oc["image"] = Image.open("templates/" + template["image"]).convert("RGB")
    oc["sex"] = template["gender"]
    oc["species"] = template["species"]
    oc["age"] = max([int(round(random.gauss(21, 6))), 13])

    # Give it a name
    if oc["sex"] == "female":
        oc["name"] = random.choice(NAMES_FEMALE)
    elif oc["sex"] == "male":
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

    oc["stats"] = getOCStats()
    oc["info"] = markov.getRandomParagraph("text/descs.sqlite3", sentences=random.randrange(3,7))

    return oc

def getOCDescription(oc):
    oc_desc = oc["name"] + " the " + oc["species"].title() + "\n\n"
    oc_desc += oc["info"] + "\n\n"
    # oc_desc += "Name: " + oc["name"] + "\n"
    # oc_desc += "Species: " + oc["species"].title() + "\n"
    oc_desc += "Age: " + str(oc["age"]) + "\n"
    oc_desc += "Sex: " + oc["sex"].title() + "\n"
    oc_desc += "Personality: " + oc["personality"].title() + "\n"
    oc_desc += "Skills/Passions: " + ", ".join(oc["skills"]).title() + "\n"
    for k,v in sorted(oc.iteritems()):
        if k not in ["name", "gender", "image", "species", "age", "personality", "skills", "stats", "info"]:
            oc_desc += k.title() + " Color: " + v.title() + "\n"
    oc_desc += "\n"
    for k,v in sorted(oc["stats"].iteritems()):
        oc_desc += k + ": " + str(v) + "/10\n"
    return oc_desc[0:-1] # Removing the final newline
