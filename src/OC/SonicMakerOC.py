from collections import OrderedDict
import json
import os
import random
from PIL import Image
from typing import Callable, ClassVar

from .OC import OC
import src.Util.ColorUtil as ColorUtil
import src.Util.ImageUtil as ImageUtil
import src.Directories as Directories


def _json_load_or_fallback(filepath: str, fallback_factory: Callable) -> OrderedDict:
    if os.path.exists(filepath):
        try:
            with open(filepath) as f:
                return json.load(f, object_pairs_hook=OrderedDict)
        except json.JSONDecodeError:
            print(f"JSON decode error reading {f}, falling back to empty dict")
            return fallback_factory()
    else:
        print(f"{f} does not exist, falling back to empty dict")
        return fallback_factory()


class SonicMakerOC(OC):
    SONICMAKER_FILL: ClassVar[OrderedDict]
    """Data that contains information on how to create and fill the regions of the OC.

    `data/sonicmaker-fill.json` is a JSON file in the following format:

    ```
    {
        "image-size": [<template-width>, <template-height>],
        "part-1": {
            "optional": <true|false>,
            "position": [<x-coord of this part>, <y-coord of this part>],
            "fill": {
                "type-1": {
                    "fill-operation": {
                        "region-name-1": [ [<fill x-coord 1>, <fill y-coord 1>], [<fill x-coord 2>, <fill y-coord 2>], ... ],
                        "region-name-2": [ ... ],
                        ...
                    },
                    "another-fill-op": { ... },
                    ...
                },
                "type-2": { ... },
                ...
            }
        },
        "part-2": { ... },
        ...
    }
    ```

    Explanation for each part:

    - `image-size`: Dimensions of the image to generate in pixels.
    - `part-1`: Which body part to place. Images for this should be placed in `/images/sonicmaker/part-1-{type}.png` and should all be the same size.
      Note that these parts will be placed in sequential order; i.e., `part-1` will be placed first, then `part-2`, and so on.
        - `optional`: Whether this part can randomly be omitted or not.
        - `position`: Upper-left corner of where this part should be placed.
        - `fill` contains the actual information on where to fill this part.
            - `type-1` is one of the possible types of this part to choose. This image should be placed in `/images/sonicmaker/part-1-type-1.png`.
                - `fill-operation` is what operation you want to do to the color when filling.
                  This is to account for colors that should be shaded or brightened in certain areas, for instance.
                  Below are the available types of operations:
                    - `noop` (for "no-operation")
                    - `brighten`
                    - `darken`
                    - `complementary`
                    - `analogous-ccw`
                    - `analogous-cw`
                - `region-name-1` under the operation defines the name of the region being filled (e.g., "fur" or "skin").
                  Regions stay consistently colored all throughout the OC regardless of the part it is on, and will use a skin tone if set to "skin".
                  You can also make it randomly decide between a region name using a pipe character, e.g. "fur|skin".
                  The value for this is a list of x,y coordinates indicating the points to flood fill the template at (like flood filling in MS Paint).
    """

    @classmethod
    def __initialize_fill(cls):
        cls.SONICMAKER_FILL = _json_load_or_fallback(os.path.join(Directories.DATA_DIR, "sonicmaker-fill.json"), OrderedDict)

    def generate_image(self, fill_threshold: int = 96) -> None:
        """Implements `generate_image` from `OC` by using Sonic Maker template parts.

        Parameters
        ----------
        fill_threshold : int, optional
            threshold of difference in color when flood filling, by default 96
        """
        # Make sure fill dict is initialized
        try:
            SonicMakerOC.SONICMAKER_FILL
        except AttributeError:
            SonicMakerOC.__initialize_fill()

        sonicmaker_fill = SonicMakerOC.SONICMAKER_FILL
        part_image_extension = ".png"
        image_width, image_height = sonicmaker_fill.get("image-size", [500, 500])
        image_size = (image_width, image_height)
        self._image = Image.new("RGBA", image_size, (0, 0, 0, 0))

        # region_colors will keep colors consistent for each
        region_colors = {}
        for part_name in sonicmaker_fill:
            # Since image-size has to be in the top level too, skip it
            if part_name == "image-size":
                continue

            part = sonicmaker_fill[part_name]

            omit_part = random.choice((True, False)) if part.get("optional", False) else False

            # If optional part randomly omitted, skip it
            if omit_part:
                continue

            part_types = list(part.get("fill", {}).keys())

            # If no types defined for this part, skip it
            if len(part_types) == 0:
                continue

            type_name = random.choice(part_types)
            type_img = Image.open(os.path.join(Directories.IMAGES_DIR, "sonicmaker", f"{part_name}-{type_name}{part_image_extension}")).convert("RGBA")
            fill_ops = part["fill"][type_name]

            # Now start filling with the list of coords to fill
            for operation in fill_ops:
                op_func: Callable[[ColorUtil.ColorTuple], ColorUtil.ColorTuple] = OC._TRANSFORM_OPS.get(operation, lambda color: color)
                op_regions = fill_ops[operation]
                for region_name in op_regions:
                    # If there is a pipe, randomly pick one of the region types
                    if "|" in region_name:
                        current_region = random.choice(region_name.split("|"))
                    else:
                        current_region = region_name

                    # Give the current region a color if it doesn't have one
                    if current_region not in region_colors:
                        if current_region == "skin":
                            # Use skin tone gradient image to get a skin tone, and slightly randomize it
                            new_color_rgb = ColorUtil.randomize_color(ImageUtil.get_random_color_from_image(ColorUtil.SKIN_TONE_GRADIENT))
                            new_color_name = ColorUtil.get_nearest_color_in_colors_list(new_color_rgb, ColorUtil.SKIN_TONE_COLORS)["name"]
                        else:
                            # Get a random color from general colors list and slightly randomize it
                            new_color = random.choice(ColorUtil.GENERAL_COLORS)
                            new_color_rgb = ColorUtil.randomize_color(new_color["color"])
                            new_color_name = new_color["name"]

                        # Now set this region to use this color throughout the whole OC
                        region_colors[current_region] = new_color_rgb
                        self._color_regions[current_region] = new_color_name

                    fill_rgb = op_func(region_colors[current_region])
                    coords = op_regions[region_name]

                    # Fill each coordinate with the color we got, with the proper transformation
                    for coord in coords:
                        coord_x, coord_y = coord
                        fill_r, fill_g, fill_b = fill_rgb
                        fill_color = (int(fill_r), int(fill_g), int(fill_b))
                        ImageUtil.multiply_floodfill(type_img, (coord_x, coord_y), fill_color, threshold=fill_threshold)

            # Finally, paste this region in the overall image
            self._image.paste(type_img, part.get("position", (0, 0)), type_img)
