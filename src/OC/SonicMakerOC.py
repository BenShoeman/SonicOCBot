import numpy as np
from PIL import Image
from typing import ClassVar

from .OC import OC
import src.Directories as Directories
from src.FillStrategy import create_fill_strategy_for_species
import src.Util.FileUtil as FileUtil


_rng = np.random.default_rng()


class SonicMakerOC(OC):
    SONICMAKER_FILL: ClassVar[dict]
    """Data that contains information on how to create and fill the regions of the OC.

    `data/sonicmaker-fill.yml` is a YAML file in the following format:

    ```
    image-size: [<template-width>, <template-height>]
    part-1:
        optional: <true|false>
        position: [<x-coord of this part>, <y-coord of this part>]
        fill:
            type-1:
                fill-operation:
                    region-name-1: [ [<fill x-coord 1>, <fill y-coord 1>], [<fill x-coord 2>, <fill y-coord 2>], ... ]
                    region-name-2: [ ... ]
                    ...
                another-fill-op:
                    ...
                ...
            type-2:
                ...
            ...
    part-2:
        ...
    ...
    ```

    Explanation for each part:

    - `image-size`: Dimensions of the image to generate in pixels.
    - `part-1`: Which body part to place. Images for this should be placed in `/images/sonicmaker/part-1-{type}.png` and should all be the same size.
      Note that these parts will be placed in sequential order; i.e., `part-1` will be placed first, then `part-2`, and so on.
        - `optional`: Whether this part can randomly be omitted or not.
        - `position`: Upper-left corner of where this part should be placed.
        - `fill` contains the actual information on where to fill this part.
            - `type-1` is one of the possible types of this part to choose. This image should be placed in `/images/sonicmaker/part-1-type-1.png`.
                - If you want no fill, leave this field blank (i.e. null).
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
    def __initialize_fill(cls) -> None:
        cls.SONICMAKER_FILL = FileUtil.yaml_load(Directories.DATA_DIR / "sonicmaker-fill.yml")

    def generate_image(self, fill_threshold: int = 192) -> None:
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

        species_type: dict = OC._SPECIES[self.species].get("type")
        type_parts: dict = OC._SPECIES_PARTS.get(species_type, {})
        use_skin_tones = type_parts.get("use-skin-tones", True)
        rename_map = type_parts.get("rename", {})
        allow_parts: dict = type_parts.get("allow", {})
        deny_parts: dict = type_parts.get("deny", {})
        omit_list = type_parts.get("omit", [])

        sonicmaker_fill = SonicMakerOC.SONICMAKER_FILL
        part_image_extension = ".png"
        image_width, image_height = sonicmaker_fill.get("image-size", [500, 500])
        self._image = Image.new("RGBA", (image_width, image_height), (0, 0, 0, 0))

        for part_name, part in sonicmaker_fill.get("fills", {}).items():
            # Always skip parts in the omit list
            if part_name in omit_list:
                continue

            # Remove or include parts based on the allow/deny lists
            allow_list = allow_parts.get(part_name, list(part.get("fill", {}).keys()))
            deny_list = deny_parts.get(part_name, [])
            part_types = [typ for typ in part.get("fill", {}).keys() if typ in allow_list and typ not in deny_list]

            # If required, do not allow the part to be omitted unless explicitly in the omit list
            if part.get("required", False) and "none" in part_types:
                part_types.remove("none")

            try:
                type_name = _rng.choice(part_types)
            except ValueError:
                # Means the list is empty, so skip this part
                continue
            else:
                # If we chose to omit this part, skip it
                if type_name == "none":
                    continue

            type_img_arr = np.asarray(Image.open(Directories.IMAGES_DIR / "sonicmaker" / f"{part_name}-{type_name}{part_image_extension}").convert("RGBA"))
            fill_ops = part["fill"][type_name] or {}  # Coalesce to empty dict if None

            # Now start filling with the list of coords to fill
            for operation, op_regions in fill_ops.items():
                for region_name, coords in op_regions.items():
                    # Randomly pick one of the region types if there is a pipe
                    current_region = _rng.choice(region_name.split("|")) if "|" in region_name else region_name

                    # If animal types config says to rename, then do so; otherwise go with this name
                    current_region = rename_map.get(current_region, current_region)

                    # Give the current region type a fill strategy if it doesn't have one
                    if current_region not in self._fill_regions:
                        self._fill_regions[current_region] = create_fill_strategy_for_species(
                            current_region, self.species, threshold=fill_threshold, use_skin_tones=use_skin_tones
                        )

                    # Fill each coordinate with the color we got, with the proper transformation
                    fill_strategy = self._fill_regions[current_region]
                    for coord in coords:
                        fill_strategy.floodfill(type_img_arr, coord, transform_type=operation)

            # Finally, paste this region in the overall image using alpha composite (for more accurate alpha blending)
            type_img = Image.new("RGBA", self._image.size, color=(0, 0, 0, 0))
            temp_img = Image.fromarray(type_img_arr)
            type_img.paste(temp_img, part.get("position", (0, 0)), temp_img)
            self._image = Image.alpha_composite(self._image, type_img)
