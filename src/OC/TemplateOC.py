import numpy as np
import os
import random
from PIL import Image, ImageDraw
from typing import Callable, ClassVar, Optional
import yaml

from .OC import OC
import src.Directories as Directories
from src.FillStrategy import ColorFill
import src.Util.FileUtil as FileUtil


class TemplateOC(OC):
    TEMPLATES: ClassVar[dict]
    """Data that contains information on how to create and fill the regions of the OC.

    `data/template-fill.yml` is a YAML file in the following format:

    ```
    template-1:
        species: <species-name>
        gender: <gender letter or string>
        fill:
            fill-operation:
                region-name-1: [ [<fill x-coord 1>, <fill y-coord 1>], [<fill x-coord 2>, <fill y-coord 2>], ... ]
                region-name-2: [ ... ]
                ...
            another-fill-op:
                ...
            ...
    template-2:
        ...
    ...
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
        """Create a `TemplateOC`, optionally with a template name.

        Parameters
        ----------
        template_name : Optional[str], optional
            if not None, use the template defined here, by default None
        auto_populate : bool, optional
            whether all the fields should be automatically populated, by default True
        """
        # Make sure template dict is initialized
        try:
            TemplateOC.TEMPLATES
        except AttributeError:
            TemplateOC.__initialize_templates()

        if template_name is None:
            self.__template_name = random.choice(list(TemplateOC.TEMPLATES.keys()))
        else:
            self.__template_name = template_name
        self.__template = TemplateOC.TEMPLATES[self.__template_name]
        super().__init__(auto_populate=auto_populate)

    @classmethod
    def __initialize_templates(cls):
        cls.TEMPLATES = FileUtil.yaml_load_or_fallback(os.path.join(Directories.DATA_DIR, "template-fill.yml"))

    def generate_image(self, fill_threshold: int = 192) -> None:
        """Implements `generate_image` from `OC` by using full templates.

        Parameters
        ----------
        fill_threshold : int, optional
            threshold of difference in color when flood filling, by default 96
        """
        part_image_extension = ".png"
        img_arr = np.asarray(Image.open(os.path.join(Directories.IMAGES_DIR, "template", self.__template_name + part_image_extension)).convert("RGBA"))

        # Fill each region in with a random color
        fill_ops = self.__template["fill"]
        for operation in fill_ops:
            op_regions = fill_ops[operation]
            for region_name in op_regions:
                if region_name not in self._fill_regions:
                    region_fill = ColorFill(region_name, threshold=fill_threshold)
                    # Now set this region to use this color throughout the whole OC
                    self._fill_regions[region_name] = region_fill

                fill_strategy = self._fill_regions[region_name]
                coords = op_regions[region_name]
                for coord in coords:
                    fill_strategy.floodfill(img_arr, coord, transform_type=operation)

        self._image = Image.fromarray(img_arr)

    def _generate_gender(self):
        self._gender = self.__template["gender"]

    def _generate_species(self):
        self._species = self.__template["species"]
