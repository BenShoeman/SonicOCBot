import json
import random
import re
from collections import OrderedDict
from PIL import Image, ImageDraw
from colors import *
from stats import *
import markov

TEMPLATEFILLINFO = json.loads(open("templates/fillinfo.json").read())
SONICMAKERINFO = json.loads(open("sonicmaker/info.json").read(), object_pairs_hook=OrderedDict)

NAMES_FEMALE = [x.replace("\n","") for x in open("data/names_female.txt").readlines()]
NAMES_MALE = [x.replace("\n","") for x in open("data/names_male.txt").readlines()]
SPECIES = [x.replace("\n","") for x in open("data/animals.txt").readlines()]
PERSONALITIES = [x.replace("\n","") for x in open("data/personalities.txt").readlines()]
SKILLS = [x.replace("\n","") for x in open("data/skills.txt").readlines()]

GENERAL_COLORS = getColorsList("data/generalcolors.txt")
SKIN_TONES = getColorsList("data/skintones.txt")

def createOC(n_original = 0.6):
    if random.uniform(0,1) < n_original:
        return createOCFromSonicMaker()
    else:
        return createOCFromTemplate()

def createOCFromTemplate(templatenum = -1): # templatenum is for debug purposes
    oc = {}

    if templatenum < 0:
        # Picking a random template to use
        template = random.choice(TEMPLATEFILLINFO["templates"])
    else:
        template = TEMPLATEFILLINFO["templates"][templatenum]

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
    skillsnum = int(max([1, random.gauss(2.5, 2)]))
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
    if oc["sex"] == "male":
        oc["info"] = markov.getRandomParagraph("text/malocdescs.sqlite3", sentences=random.randrange(3,7))
    else:
        oc["info"] = markov.getRandomParagraph("text/femocdescs.sqlite3", sentences=random.randrange(3,7))

    return oc

def createOCFromSonicMaker(bodynum = None):
    oc = {}
    selectioninfo = {}

    # Get base for image
    if not bodynum:
        bodynum = random.randrange(1,SONICMAKERINFO["regions"]["body"]["number"]+1)
    oc["image"] = Image.open("sonicmaker/body-" + str(bodynum) + ".png").convert("RGB")
    oc["sex"] = random.choice(["male", "female"])
    oc["species"] = random.choice(SPECIES)
    oc["age"] = max([int(round(random.gauss(21, 6))), 13])

    # Give it a name
    if oc["sex"] == "female":
        oc["name"] = random.choice(NAMES_FEMALE)
    elif oc["sex"] == "male":
        oc["name"] = random.choice(NAMES_MALE)

    oc["personality"] = random.choice(PERSONALITIES)

    oc["skills"] = []
    skillsnum = int(max([1, random.gauss(2.5, 2)]))
    for i in range(skillsnum):
        newskill = random.choice(SKILLS)
        if newskill not in oc["skills"]:
            oc["skills"].append(newskill)

    fillregions = {}
    for reg in SONICMAKERINFO["regions"]:
        if "numbermin" in SONICMAKERINFO["regions"][reg]: minim = SONICMAKERINFO["regions"][reg]["numbermin"]
        else: minim = 0
        imgnum = bodynum if reg == "body" else random.randrange(minim,SONICMAKERINFO["regions"][reg]["number"]+1)

        if imgnum > 0:
            selectioninfo[reg] = imgnum
            currimg = oc["image"] if reg == "body" else Image.open("sonicmaker/" + reg + "-" + str(imgnum) + ".png").convert("RGBA")

            for area in SONICMAKERINFO["regions"][reg]["fill"]:
                # determine if it's a general fill region or specific to numbered template
                num = re.search(r'^\d+', area)
                if num:
                    num = int(num.group(0))
                    if num != imgnum:
                        continue
                    fillarea = random.choice(re.search(r':(\w*)$',area).group(1).split("/"))
                else:
                    fillarea = random.choice(area.split("/"))

                if fillarea not in fillregions:
                    if fillarea == "skin":
                        fillregions[fillarea] = random.choice(SKIN_TONES)
                    else:
                        fillregions[fillarea] = random.choice(GENERAL_COLORS)
                    oc[fillarea] = fillregions[fillarea]["name"]
                    fillregions[fillarea]["color"] = randomizeColor(fillregions[fillarea]["color"])
                clr = fillregions[fillarea]["color"]

                for coord in SONICMAKERINFO["regions"][reg]["fill"][area]:
                    if ":tint:" in area:
                        ImageDraw.floodfill(currimg, tuple(coord), brightenColor(clr))
                    elif ":shade:" in area:
                        ImageDraw.floodfill(currimg, tuple(coord), darkenColor(clr))
                    elif ":complement:" in area:
                        ImageDraw.floodfill(currimg, tuple(coord), complementaryColor(clr))
                    elif ":analogccw:" in area:
                        ImageDraw.floodfill(currimg, tuple(coord), analogousCCWColor(clr))
                    elif ":analogcw:" in area:
                        ImageDraw.floodfill(currimg, tuple(coord), analogousCWColor(clr))
                    else:
                        ImageDraw.floodfill(currimg, tuple(coord), clr)

            if reg != "body":
                oc["image"].paste(currimg, tuple(SONICMAKERINFO["regions"][reg]["position"]), currimg)

    oc["stats"] = getOCStats()
    if oc["sex"] == "male":
        oc["info"] = markov.getRandomParagraph("text/malocdescs.sqlite3", sentences=random.randrange(3,7))
    else:
        oc["info"] = markov.getRandomParagraph("text/femocdescs.sqlite3", sentences=random.randrange(3,7))

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
        if k not in ["name", "sex", "image", "species", "age", "personality", "skills", "stats", "info"]:
            oc_desc += k.title() + " Color: " + v.title() + "\n"
    oc_desc += "\n"
    for k,v in sorted(oc["stats"].iteritems()):
        oc_desc += k + ": " + str(v) + "/10\n"
    return oc_desc[0:-1] # Removing the final newline
