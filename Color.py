from math import atan2, cos, sin, pi
import random
import re

# rgb2hsl and hsl2rgb receive a 3-tuple of colors in RGB or HSL and return a
# 3-tuple of colors. RGB values are in [0,255], Hue values are in [0,360) and
# Saturation/Lightness values are in [0,100].

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

    # Return HSL values in the range [0,360) for hue, [0,100] for sat./lightness
    return (round(h,1),round(s*100,2),round(l*100,2))

def hsl2rgb(hsl):
    # Get saturation and lightness in range [0,1]
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

    # Return RGB values in the range [0,255]
    return (int(round((r+m)*255)), int(round((g+m)*255)), int(round((b+m)*255)))

# Colors list file is in following format:
# RRR GGG BBB color name
def get_colors_list(filename):
    colors = []
    with open(filename, 'r') as f:
        for line in f:
            if line.strip() != "":
                color_info = line.split()
                curr_color = (int(color_info[0]), int(color_info[1]), int(color_info[2]))
                curr_name = " ".join(color_info[3:])
                colors.append({"name": curr_name, "color": curr_color})
    return colors

# Allow n within range [min_val, max_val]. If it exceeds either bound, set it to
# the closest extreme of the boundary.
def to_within_range(n, min_val, max_val):
    if n < min_val: return min_val
    elif n > max_val: return max_val
    else: return n

def randomize_color(rgb):
    h, s, l = rgb2hsl(rgb)
    # Randomize lightness more the closer it is to 50%.
    rand_light_factor = 1 - ((l-50)/50)**2
    new_hsl = (
        h + random.random()*16 - 8,
        to_within_range(s + random.gauss(0,2.5), 0, 100),
        to_within_range(l + random.gauss(0,2.5)*rand_light_factor, 0, 100)
    )
    return hsl2rgb(new_hsl)

def darken_color(rgb, amount=10):
    h, s, l = rgb2hsl(rgb)
    new_hsl = (h, s, to_within_range(l-amount, 0, 100))
    return hsl2rgb(new_hsl)

def brighten_color(rgb, amount=10):
    h, s, l = rgb2hsl(rgb)
    new_hsl = (h, s, to_within_range(l+amount, 0, 100))
    return hsl2rgb(new_hsl)

def complementary_color(rgb):
    h, s, l = rgb2hsl(rgb)
    new_hsl = ((h + 180) % 360, s, l)
    return hsl2rgb(new_hsl)

def analogous_ccw_color(rgb):
    h, s, l = rgb2hsl(rgb)
    new_hsl = ((h + 30) % 360, s, l)
    return hsl2rgb(new_hsl)

def analogous_cw_color(rgb):
    h, s, l = rgb2hsl(rgb)
    new_hsl = ((h - 30) % 360, s, l)
    return hsl2rgb(new_hsl)
