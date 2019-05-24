from abc import ABC, abstractmethod
from collections import OrderedDict
import json
import os
from PIL import Image, ImageDraw
import random

import Color
import Directories
from SQLiteMarkovModel import SQLiteMarkovModel

class OC(ABC):
    _NAMES_WOMAN = [line.strip() for line in open(os.path.join(Directories.DATA_DIR, "names_woman.txt"))]
    _NAMES_MAN = [line.strip() for line in open(os.path.join(Directories.DATA_DIR, "names_man.txt"))]
    _SPECIES = [line.strip() for line in open(os.path.join(Directories.DATA_DIR, "animals.txt"))]
    _PERSONALITIES = [line.strip() for line in open(os.path.join(Directories.DATA_DIR, "personalities.txt"))]
    _SKILLS = [line.strip() for line in open(os.path.join(Directories.DATA_DIR, "skills.txt"))]

    _GENERAL_COLORS = Color.get_colors_list(os.path.join(Directories.DATA_DIR, "generalcolors.txt"))
    _SKIN_TONES = Color.get_colors_list(os.path.join(Directories.DATA_DIR, "skintones.txt"))

    _DESCS_MAN = SQLiteMarkovModel(os.path.join(Directories.MODELS_DIR, "ocdescs_man.sqlite3"))
    _DESCS_WOMAN = SQLiteMarkovModel(os.path.join(Directories.MODELS_DIR, "ocdescs_woman.sqlite3"))

    _TRANSFORM_MAP = {
        "norm": lambda color: color,
        "shade": lambda color: Color.darken_color(color),
        "tint": lambda color: Color.brighten_color(color),
        "complement": lambda color: Color.complementary_color(color),
        "analogccw": lambda color: Color.analogous_ccw_color(color),
        "analogcw": lambda color: Color.analogous_cw_color(color),
    }

    def __init__(self):
        self._generate_gender()
        self._generate_species()
        self._generate_age()
        self._generate_name()
        self._generate_personality()
        self._generate_height()
        self._generate_weight()
        self._generate_skills()
        self._generate_description()
        self._color_regions = {}
        self._generate_image()
    
    @property
    def name(self): return self._name
    @property
    def species(self): return self._species
    @property
    def age(self): return self._age
    @property
    def gender(self): return self._gender
    @property
    def personality(self): return self._personality
    @property
    def height(self): return self._height
    @property
    def weight(self): return self._weight
    @property
    def skills(self): return tuple(self._skills)
    @property
    def description(self): return self._description
    @property
    def image(self): return self._image.copy()
    @property
    def color_regions(self): return self._color_regions.copy()

    # generate_image must define self._image and self._color_regions, where
    # self._image is a Pillow Image and self._color_regions is a dict of region
    # names to color names, e.g. {"fur": "red"}  
    @abstractmethod
    def _generate_image(self):
        pass
    
    def _generate_gender(self):
        self._gender = random.choice(("man", "woman"))
    
    def _generate_species(self):
        self._species = random.choice(OC._SPECIES)
    
    def _generate_age(self):
        self._age = max([int(round(random.gauss(21, 6))), 13])
    
    def _generate_name(self):
        if self._gender == "woman":
            self._name = random.choice(OC._NAMES_WOMAN)
        elif self._gender == "man":
            self._name = random.choice(OC._NAMES_MAN)
        else:
            self._name = random.choice(OC._NAMES_WOMAN + OC._NAMES_MAN)
    
    def _generate_personality(self):
        self._personality = random.choice(OC._PERSONALITIES)
    
    def _generate_height(self):
        feet = round(random.gauss(5,1.25))
        inches = round(random.randint(0,11))
        self._height = f"{feet}'{inches}"
    
    # Assumes standard height string in format FT'IN
    def _generate_weight(self):
        feet, inches = self._height.split("'")
        inches_from_avg = int(feet)*12 + int(inches) - 66
        weight = round(random.gauss(136, 18) +
            random.gauss(4, 0.25) * inches_from_avg)
        self._weight = f"{weight} lbs."
    
    def _generate_skills(self):
        self._skills = []
        num_skills = int(max([1, random.gauss(2.5, 1)]))
        for _ in range(num_skills):
            new_skill = random.choice(OC._SKILLS)
            if new_skill not in self._skills:
                self._skills.append(new_skill)
    
    def _generate_description(self):
        sentences = random.randint(2,4)
        if self._gender == "woman":
            model = OC._DESCS_WOMAN
        elif self._gender == "man":
            model = OC._DESCS_MAN
        else:
            model = random.choice([OC._DESCS_WOMAN, OC._DESCS_MAN])
        self._description = model.get_random_paragraph(sentences=sentences)

    @staticmethod
    def generate_oc(pr_original=0.8):
        if random.random() < pr_original:
            return SonicMakerOC()
        else:
            return TemplateOC()

class SonicMakerOC(OC):
    __SONICMAKER_FILL = json.load(
        open(os.path.join(Directories.SONICMAKER_DIR, "fill.json")),
        object_pairs_hook=OrderedDict
    )
    
    def _generate_image(self):
        self._image = Image.new("RGBA", (454, 649), (0,0,0,0))
        # Fill each region in with a random color, but keep colors consistent
        # thru part_colors
        part_colors = {}
        for region_key in SonicMakerOC.__SONICMAKER_FILL:
            region = SonicMakerOC.__SONICMAKER_FILL[region_key]
            # Include 0 if optional. 0 indicates that we shouldn't add the part
            img_num = random.randint(
                0 if region["optional"] else 1, region["count"]
            )
            if img_num > 0:
                current_img = Image.open(
                    os.path.join(Directories.SONICMAKER_DIR, f"{region_key}-{img_num}.png")
                ).convert("RGBA")
                # Only fill if we have stuff to fill
                if str(img_num) in region["fill"]:
                    fill_coords = region["fill"][str(img_num)]
                    # Now we can start filling, now that we have the list of coords
                    # and parts to fill
                    for part, coords in fill_coords.items():
                        # If we have a pipe (|), then we need to randomly pick one
                        # of the parts
                        if '|' in part:
                            part = random.choice(part.split('|'))
                        
                        # If we have a color transformation, get that info and
                        # remove it from the part name
                        transform_idx = part.rfind(';')
                        if transform_idx >= 0:
                            fill_typ = part[transform_idx+1:]
                            part = part[:transform_idx]
                        # Otherwise, just set transformation to norm (no adjustment)
                        else:
                            fill_typ = "norm"
                        
                        # Give the part a color if it doesn't have one
                        if part not in part_colors:
                            if part == "skin":
                                new_color = random.choice(OC._SKIN_TONES)
                            else:
                                new_color = random.choice(OC._GENERAL_COLORS)
                            # Slightly randomize the color to make it unique
                            part_colors[part] = Color.randomize_color(new_color["color"])
                            self._color_regions[part] = new_color["name"]
                        fill_color = part_colors[part]

                        # Fill each coordinate with the color we got, with the
                        # proper transformation
                        for coord in coords:
                            # Need to add alpha component to color, hence +(255,)
                            ImageDraw.floodfill(
                                current_img, tuple(coord),
                                OC._TRANSFORM_MAP[fill_typ](fill_color) + (255,)
                            )
                # Finally, paste this region in the overall image
                self._image.paste(current_img, region["position"], current_img)
        # Resize image to have height of 500px
        width, height = self._image.size
        resz_ratio = 500 / height
        self._image = self._image.resize((int(width*resz_ratio), 500), Image.BICUBIC)

class TemplateOC(OC):
    __TEMPLATES = json.load(open(os.path.join(Directories.TEMPLATES_DIR, "fill.json")))
    
    def __init__(self, template_num=-1):
        if template_num < 0:
            self.__template = random.choice(TemplateOC.__TEMPLATES)
        else:
            self.__template = TemplateOC.__TEMPLATES[template_num]
        super().__init__()
    
    def _generate_image(self):
        self._image = Image.open(
            os.path.join(Directories.TEMPLATES_DIR, self.__template['image'])
        ).convert("RGBA")
        # Fill each region in with a random color
        for region in self.__template["fill"]:
            if region["region"] == "skin":
                region_color = random.choice(OC._SKIN_TONES)
            else:
                region_color = random.choice(OC._GENERAL_COLORS)
            # Add text name description
            self._color_regions[region["region"]] = region_color["name"]
            # Slightly randomize the color to make it unique
            fill_color = Color.randomize_color(region_color["color"])
            for fill_typ in OC._TRANSFORM_MAP.keys():
                coords = region.get("coords-" + fill_typ)
                if coords is not None:
                    for coord in coords:
                        # Need to add alpha component to color, hence +(255,)
                        ImageDraw.floodfill(
                            self._image, tuple(coord),
                            OC._TRANSFORM_MAP[fill_typ](fill_color) + (255,)
                        )
        # Resize image to have height of 500px
        width, height = self._image.size
        resz_ratio = 500 / height
        self._image = self._image.resize((int(width*resz_ratio), 500), Image.BICUBIC)
    
    def _generate_gender(self):
        self._gender = self.__template["gender"]
    
    def _generate_species(self):
        self._species = self.__template["species"]