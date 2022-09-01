import numpy as np
from typing import Callable, ClassVar, Optional

from .FillStrategy import FillStrategy
import src.Util.ColorUtil as ColorUtil
import src.Util.ImageUtil as ImageUtil


_rng = np.random.default_rng()


class ColorFill(FillStrategy):
    """FillStrategy that fills on a single color."""

    _TRANSFORM_OPS: ClassVar[dict[str, Callable[[ColorUtil.ColorTuple], ColorUtil.ColorTuple]]] = {
        "noop": lambda color: color,
        "darken": ColorUtil.darken,
        "brighten": ColorUtil.brighten,
        "complementary": ColorUtil.complementary,
        "analogous-ccw": ColorUtil.analogous_ccw,
        "analogous-cw": ColorUtil.analogous_cw,
    }
    """Dict mapping transformation operations to `ColorUtil` functions."""

    def __init__(
        self,
        region_type: str,
        color: Optional[ColorUtil.ColorTuple] = None,
        threshold: int = 192,
        multiply_fill: bool = True,
    ):
        """Create a `ColorFill` strategy, optionally with a specific color.

        Parameters
        ----------
        region_type : str
            type of region to fill (e.g., "fur" or "skin")
        color : Optional[ColorTuple], optional
            if given, sets the `ColorFill` to use this specific color
        threshold : int, optional
            floodfill threshold when comparing colors to the floodfill origin, by default 192
        multiply_fill : bool, optional
            if True, does a multiply blend on the fill instead of a regular floodfill, by default True
        """
        super().__init__(region_type)
        color_list = ColorUtil.SKIN_TONE_COLORS if self._region_type == "skin" else ColorUtil.GENERAL_COLORS
        if color:
            self._fill = color
            self._color_name = ColorUtil.get_nearest_color_in_colors_list(self._fill, color_list)["name"]
        else:
            # Randomly pick a color from the color list depending on region type
            if self._region_type == "skin":
                self._fill = ColorUtil.randomize_color(ImageUtil.get_random_color_from_image(ColorUtil.SKIN_TONE_GRADIENT))
                self._color_name = ColorUtil.get_nearest_color_in_colors_list(self._fill, color_list)["name"]
            else:
                new_color = _rng.choice(ColorUtil.GENERAL_COLORS)
                self._fill = ColorUtil.randomize_color(new_color["color"])
                self._color_name = new_color["name"]
        self._threshold = threshold
        self._multiply_fill = multiply_fill

    @property
    def fill_type(self) -> str:
        """Type of the fill, "color"."""
        return "color"

    @property
    def fill_name(self) -> str:
        """Name of the fill (e.g., "red")."""
        return self._color_name

    def floodfill(self, img: np.ndarray, xy: tuple[int, int], transform_type: str = "noop") -> None:
        """Implements `floodfill` by filling the region with this `ColorFill`.

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
        fill = ColorFill._TRANSFORM_OPS.get(transform_type, lambda color: color)(self._fill)
        if self._multiply_fill:
            ImageUtil.multiply_floodfill(img, xy, fill, threshold=self._threshold, in_place=True)
        else:
            ImageUtil.floodfill(img, xy, fill, threshold=self._threshold, in_place=True)
