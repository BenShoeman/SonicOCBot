import numpy as np
import os
import glob
from pathlib import Path
from PIL import Image, ImageChops
from typing import Callable, ClassVar, Optional

from .FillStrategy import FillStrategy
import src.Directories as Directories
import src.Util.ColorUtil as ColorUtil
import src.Util.FileUtil as FileUtil
import src.Util.ImageUtil as ImageUtil


_rng = np.random.default_rng()


class PatternFill(FillStrategy):
    """FillStrategy that fills on a pattern."""

    _TRANSFORM_OPS: ClassVar[dict[str, Callable[[np.ndarray], np.ndarray]]] = {
        "noop": lambda img: img,
        "darken": ColorUtil.darken,
        "brighten": ColorUtil.brighten,
        "complementary": ColorUtil.complementary,
        "analogous-ccw": ColorUtil.analogous_ccw,
        "analogous-cw": ColorUtil.analogous_cw,
    }
    """Dict mapping transformation operations to `ColorUtil` functions."""

    PATTERN_PROBABILITIES: ClassVar[dict] = FileUtil.yaml_load_or_fallback(os.path.join(Directories.DATA_DIR, "patterns.yml"))
    """Contains probabilities for each species to have a certain pattern."""

    def __init__(
        self,
        region_type: str,
        bg_color: Optional[ColorUtil.ColorTuple] = None,
        fg_color: Optional[ColorUtil.ColorTuple] = None,
        pattern_type: Optional[str] = None,
        threshold: int = 192,
        multiply_fill: bool = True,
    ):
        """Create a `PatternFill` strategy, optionally with a specific pattern.

        Parameters
        ----------
        region_type : str
            type of region to fill (e.g., "fur" or "skin")
        bg_color : Optional[ColorTuple], optional
            if given, sets the `PatternFill` to use this specific color for the background
        fg_color : Optional[ColorTuple], optional
            if given, sets the `PatternFill` to use this specific color for the foreground
        pattern_type : Optional[str], optional
            if given, sets the `PatternFill` to use a specific pattern image in the foreground
        threshold : int, optional
            floodfill threshold when comparing colors to the floodfill origin, by default 192
        multiply_fill : bool, optional
            if True, does a multiply blend on the fill instead of a regular floodfill, by default True
        """
        super().__init__(region_type)

        color_list = ColorUtil.SKIN_TONE_COLORS if self._region_type == "skin" else ColorUtil.GENERAL_COLORS
        if bg_color:
            bg_fill = bg_color
            self._color_name = ColorUtil.get_nearest_color_in_colors_list(bg_fill, color_list)["name"]
        else:
            # Randomly pick a color from the color list depending on region type
            if self._region_type == "skin":
                bg_fill = ColorUtil.randomize_color(ImageUtil.get_random_color_from_image(ColorUtil.SKIN_TONE_GRADIENT))
                self._bg_color_name = ColorUtil.get_nearest_color_in_colors_list(bg_fill, color_list)["name"]
            else:
                new_color = _rng.choice(ColorUtil.GENERAL_COLORS)
                bg_fill = ColorUtil.randomize_color(new_color["color"])
                self._bg_color_name = new_color["name"]
        if fg_color:
            fg_fill = fg_color
            self._fg_color_name = ColorUtil.get_nearest_color_in_colors_list(fg_fill, color_list)["name"]
        else:
            # Randomly pick a color from the color list regardless of region type
            new_color = _rng.choice(ColorUtil.GENERAL_COLORS)
            fg_fill = ColorUtil.randomize_color(new_color["color"])
            self._fg_color_name = new_color["name"]
        if not pattern_type:
            pattern_imgs = [Path(file).stem for file in glob.iglob(os.path.join(Directories.IMAGES_DIR, "pattern", "*.png"))]
            pattern_type = _rng.choice(pattern_imgs) if len(pattern_imgs) > 0 else None
        self._pattern_type = pattern_type
        pattern_img = Image.open(os.path.join(Directories.IMAGES_DIR, "pattern", f"{pattern_type}.png")).convert("RGBA") if pattern_type is not None else None
        self._set_pattern_fill(bg_fill, fg_fill, pattern_img)

        self._threshold = threshold
        self._multiply_fill = multiply_fill

    def _set_pattern_fill(self, bg_fill: ColorUtil.ColorTuple, fg_fill: ColorUtil.ColorTuple, pattern_img: Optional[Image.Image]) -> None:
        """Create the pattern fill image using background/foreground fill colors and the pattern image.

        Parameters
        ----------
        bg_fill : ColorTuple
            background fill color tuple
        fg_fill : ColorTuple
            foreground fill color tuple
        pattern_img : Optional[Image.Image]
            pattern image; if None, no pattern image is pasted
        """
        if pattern_img:
            fill = Image.new("RGB", pattern_img.size, ColorUtil.to_pil_color_tuple(bg_fill))
            # Multiply the pattern with the foreground fill
            fg_color_img = Image.new("RGBA", pattern_img.size, ColorUtil.to_pil_color_tuple(fg_fill))
            pattern_img_colorized = ImageChops.multiply(pattern_img, fg_color_img)
            fill.paste(pattern_img_colorized, (0, 0), pattern_img)
        else:
            # Just create 1x1 dummy image with background fill
            fill = Image.new("RGB", (1, 1), ColorUtil.to_pil_color_tuple(bg_fill))
        # Convert to numpy image array for later transform op use
        self._fill = np.asarray(fill)

    @property
    def fill_type(self) -> str:
        """Type of the fill, "pattern" (or if a pattern was somehow undefined, "color")."""
        return "pattern" if self._pattern_type else "color"

    @property
    def fill_name(self) -> str:
        """Name of the fill (e.g., "white with black stripes")."""
        if self._pattern_type:
            # Only get the first part if pattern has an underscore
            pattern_type = self._pattern_type.split("_")[0]
            return f"{self._bg_color_name} with {self._fg_color_name} {pattern_type}"
        else:
            return self._bg_color_name

    def floodfill(self, img: np.ndarray, xy: tuple[int, int], transform_type: str = "noop") -> None:
        """Implements `floodfill` by filling the region with this `PatternFill`.

        Parameters
        ----------
        img : np.ndarray
            image array to floodfill
        xy : tuple[int, int]
            (x,y) coordinate to floodfill
        transform_type : str
            transform operation to apply to this fill, by default "noop";
            can be one of "noop", "darken", "brighten", "complementary", "analogous-ccw", "analogous-cw"
        """
        fill = PatternFill._TRANSFORM_OPS.get(transform_type, lambda img: img)(self._fill)
        if self._multiply_fill:
            ImageUtil.multiply_floodfill(img, xy, fill, threshold=self._threshold, in_place=True)
        else:
            ImageUtil.floodfill(img, xy, fill, threshold=self._threshold, in_place=True)
