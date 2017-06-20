from math import atan2, cos, sin, pi
import random
import re

# No error checking so don't fuck up inputs.
# Both functions receive a tuple of colors in RGB or HSV and return a tuple of colors;
# outputs are appropriate for the functions.

def rgb2hsv(rgb):
    # Get RGB values and put them in range 0..1
    r = rgb[0]/255.0; g = rgb[1]/255.0; b = rgb[2]/255.0

    c = r + g + b
    if c < 1e-4:
        return (0.0, 2.0/3.0*100.0, 0.0)
    else:
        p = 2 * (b*b + g*g + r*r - g*r - b*g - b*r) ** 0.5
        h = atan2(b-g, (2*r - b - g) / 3 ** 0.5)
        s = p / (c + p)
        v = (c + p) / 3

        # Return HSV values in range 0..360 for hue, 0..100 otherwise
        return (round(h*180/pi,3), round(s*100,3), round(v*100,3))

def hsv2rgb(hsv):
    # Get HSV values and put them in range 0..1
    h = hsv[0]*pi/180; s = hsv[1]/100; v = hsv[2]/100

    r = v * (1 + s*(cos(h)-1))
    g = v * (1 + s*(cos(h+2*pi/3)-1))
    b = v * (1 + s*(cos(h-2*pi/3)-1))

    # Return RGB values in range 0..255
    return (int(round(r*255)), int(round(g*255)), int(round(b*255)))

def rgb2hsl(rgb):
    # Get RGB values and put them in range 0..1
    r = rgb[0]/255.0; g = rgb[1]/255.0; b = rgb[2]/255.0
    cmax = max([r,g,b]); cmin = min([r,g,b])
    delta = cmax - cmin

    l = (cmax + cmin) / 2
    if delta == 0:
        return (0, 0, round(l*100,2))

    s = delta / (1 - abs(2*l - 1))

    if cmax == r:
        h = 60 * (((g-b) / delta) % 6)
    elif cmax == g:
        h = 60 * (((b-r) / delta) + 2)
    else:
        h = 60 * (((r-g) / delta) + 4)

    # Return HSL values in the range 0..360 for hue, 0..100 otherwise
    return (round(h,1),round(s*100,2),round(l*100,2))

def hsl2rgb(hsl):
    # Get saturation and lightness in range 0..1
    h = float(hsl[0]); s = hsl[1]/100.0; l = hsl[2]/100.0

    c = (1 - abs(2*l - 1)) * s
    hh = float(h) / 60
    x = c * (1 - abs(hh % 2 - 1))
    m = l - c/2

    r = 0; g = 0; b = 0
    if hh >= 5:
        r = c; b = x
    elif hh >= 4:
        r = x; b = c
    elif hh >= 3:
        g = x; b = c
    elif hh >= 2:
        g = c; b = x
    elif hh >= 1:
        r = x; g = c
    else:
        r = c; g = x

    # Return RGB values in the range 0..255
    return (int(round((r+m)*255)), int(round((g+m)*255)), int(round((b+m)*255)))

def getColorsList(filename):
    colors = []
    with open(filename,"r") as f:
        for l in f.readlines():
            colorinfo = re.split(r"\s+", l.strip())
            currColor = (int(colorinfo[0]), int(colorinfo[1]), int(colorinfo[2]))
            currName = " ".join(colorinfo[3:])
            colors.append({ "name": currName, "color": currColor })
    return colors

def randomizeColor(rgb):
    try:
        hsv = rgb2hsv(rgb)
        newhsv = (hsv[0] + random.random()*16 - 8,
            min([100, max([0, hsv[1] + random.random()*10 - 5])]),
            min([100, max([0, hsv[2] + random.random()*10 - 5])]))
        return hsv2rgb(newhsv)
    except ValueError:
        return rgb

def darkenColor(rgb):
    return (max([0, rgb[0]-30]), max([0, rgb[1]-30]), max([0, rgb[2]-30]))

def brightenColor(rgb):
    return (min([255, rgb[0]+45]), min([255, rgb[1]+45]), min([255, rgb[2]+45]))

def complementaryColor(rgb):
    hsv = rgb2hsv(rgb)
    newhsv = (hsv[0] + 180, hsv[1], hsv[2])
    return hsv2rgb(newhsv)

def analogousCCWColor(rgb):
    hsv = rgb2hsv(rgb)
    newhsv = (hsv[0] + 30, hsv[1], hsv[2])
    return hsv2rgb(newhsv)

def analogousCWColor(rgb):
    hsv = rgb2hsv(rgb)
    newhsv = (hsv[0] - 30, hsv[1], hsv[2])
    return hsv2rgb(newhsv)
