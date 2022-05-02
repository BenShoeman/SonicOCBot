import json
import os
import random
from PIL import Image, ImageDraw
from typing import Callable, Optional

import src.Directories as Directories
from src.OC.OC import OC
import src.util.ColorUtil as ColorUtil
import src.util.ImageUtil as ImageUtil


def _json_load_or_fallback(filepath: str, fallback_factory: Callable) -> dict:
    if os.path.exists(filepath):
        try:
            with open(filepath) as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"JSON decode error reading {f}, falling back to empty dict")
            return fallback_factory()
    else:
        print(f"{f} does not exist, falling back to empty dict")
        return fallback_factory()


class TemplateOC(OC):
    __TEMPLATES = _json_load_or_fallback(os.path.join(Directories.DATA_DIR, "template-fill.json"), dict)
    """Data that contains information on how to create and fill the regions of the OC.

    `template-fill.json` is a JSON file in the following format:

    ```json
    {
        "template-1": {
            "species": <species-name>,
            "gender": <gender letter or string>,
            "fill": {
                "fill-operation": {
                    "region-name-1": [ [<fill x-coord 1>, <fill y-coord 1>], [<fill x-coord 2>, <fill y-coord 2>], ... ],
                    "region-name-2": [ ... ],
                    ...
                },
                "another-fill-op": { ... },
                ...
            }
        },
        "part-2": { ... },
        ...
    }
    ```

    Explanation for each part:

    - `template-1`: One of the templates. Images for this should be placed in `/images/template/template-1.png`.
        - `species`: Species of the template, e.g. "hedgehog" or "echidna".
        - `gender`: Gender of the template, either "m", "f", or "x" for man, woman, or nonbinary respectively.
          Can also use a string to indicate a few possible options, e.g. "mf" means man or woman are possible options.
        - `fill` contains the actual information on where to fill this template.
            - `fill-operation` is what operation you want to do to the color when filling. This is identical to the fill operations for `SonicMakerOC`.
    """

    def __init__(self, template_name: Optional[str] = None, auto_populate: bool = True):
        if template_name is None:
            self.__template_name = random.choice(list(TemplateOC.__TEMPLATES.keys()))
        else:
            self.__template_name = template_name
        self.__template = TemplateOC.__TEMPLATES[self.__template_name]
        super().__init__(auto_populate=auto_populate)

    def _generate_image(self, fill_threshold: int = 96) -> None:
        part_image_extension = ".png"
        self._image = Image.open(os.path.join(Directories.IMAGES_DIR, "template", self.__template_name + part_image_extension)).convert("RGBA")

        region_colors = {}
        # Fill each region in with a random color
        fill_ops = self.__template["fill"]
        for operation in fill_ops:
            op_func = OC._TRANSFORM_OPS.get(operation, lambda color: color)
            op_regions = fill_ops[operation]
            for region_name in op_regions:
                if region_name not in region_colors:
                    if region_name == "skin":
                        # Use skin tone gradient image to get a skin tone, and slightly randomize it
                        region_color_rgb = ColorUtil.randomize_color(ImageUtil.get_random_color_from_image(ColorUtil.SKIN_TONE_GRADIENT))
                        region_color_name = ColorUtil.get_nearest_color_in_colors_list(region_color_rgb, ColorUtil.SKIN_TONE_COLORS)["name"]
                    else:
                        # Get a random color from general colors list and slightly randomize it
                        region_color = random.choice(ColorUtil.GENERAL_COLORS)
                        region_color_rgb = ColorUtil.randomize_color(region_color["color"])
                        region_color_name = region_color["name"]
                    region_colors[region_name] = region_color_rgb
                    # Add text name description
                    self._color_regions[region_name] = region_color_name

                fill_rgb = op_func(region_colors[region_name])

                coords = op_regions[region_name]
                for coord in coords:
                    coord_x, coord_y = coord
                    fill_r, fill_g, fill_b = fill_rgb
                    fill_color = (int(fill_r), int(fill_g), int(fill_b))
                    ImageUtil.multiply_floodfill(self._image, (coord_x, coord_y), fill_color, threshold=fill_threshold)

    def _generate_gender(self):
        self._gender = self.__template["gender"]

    def _generate_species(self):
        self._species = self.__template["species"]
