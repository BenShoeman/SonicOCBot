#!/usr/bin/env python

from bs4 import BeautifulSoup
import requests
from unidecode import unidecode

# Suppress pointless (for my purposes) bs4 warning
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

CATEGORIES = ["A-F", "G-M", "N-Z"]

def main():
    with open("data/colors.txt","w") as f:
        for cat in CATEGORIES:
            url = "https://en.wikipedia.org/wiki/List_of_colors:_" + cat
            resp = requests.get(url)

            soup = BeautifulSoup(resp.content)

            for tr in soup.find_all("table", class_="wikitable")[0].find_all("tr"):
                colorname = tr.find_all("th")[0].get_text().lower()
                colorhex = ""
                if tr.find_all("td"):
                    colorhex = tr.find_all("td")[0].get_text()[1:]
                if colorhex != "":
                    colorR = int(colorhex[0:2], 16)
                    colorG = int(colorhex[2:4], 16)
                    colorB = int(colorhex[4:6], 16)
                    f.write("%3d %3d %3d %s\n" % (colorR, colorG, colorB, unidecode(colorname)))

if __name__=="__main__":
    main()