import facebook
import io
import pytumblr
import random
import re
from PIL import Image, ImageDraw, ImageFont
from colors import *

GENERAL_COLORS = getColorsList("data/generalcolors.txt")

def getFollowerThanksImg(num, group):
    imwidth = 400; imheight = 400

    img = Image.new("RGB", (imwidth, imheight), "white")
    draw = ImageDraw.Draw(img)
    numfontsize = 136
    numfont = ImageFont.truetype("data/AlfaSlabOne-Regular.ttf", numfontsize)
    textfont = ImageFont.truetype("data/Montserrat-Light.ttf", 36)
    thanksfont = ImageFont.truetype("data/Montserrat-Light.ttf", 72)

    count = "{:,}".format(num)

    countSize = numfont.getsize(count)
    while countSize[0] > imwidth-20:
        numfontsize -= 2
        numfont = ImageFont.truetype("data/AlfaSlabOne-Regular.ttf", numfontsize)
        countSize = numfont.getsize(count)

    uppertxtsize = textfont.getsize("we have reached")
    draw.text((imwidth/2 - uppertxtsize[0]/2, imheight/2-countSize[1]-uppertxtsize[1]),
        "we have reached", font=textfont, fill="black")

    lowertxt = group + "."
    lowertxtsize = textfont.getsize(lowertxt)
    if "," in count:
        draw.text((imwidth/2 - lowertxtsize[0]/2, imheight/2+10),
            lowertxt, font=textfont, fill="black")
    else:
        draw.text((imwidth/2 - lowertxtsize[0]/2, imheight/2+25),
            lowertxt, font=textfont, fill="black")

    thankssize = thanksfont.getsize("Thanks!")
    draw.text((imwidth/2 - thankssize[0]/2, imheight/2-thankssize[1]+countSize[1]+uppertxtsize[1]-10),
        "Thanks!", font=thanksfont, fill="black")

    countColor = random.choice(GENERAL_COLORS)["color"]
    countColor = rgb2hsl(countColor)
    countColor = hsl2rgb((countColor[0], max([60,countColor[1]]), max([35,min([75,countColor[2]])])))

    draw.text((imwidth/2 - countSize[0]/2, imheight/2 - countSize[1]), count,
        font=numfont, fill=countColor)

    return img