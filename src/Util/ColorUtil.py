"""Utilities for reading and manipulating colors.

This module has 4 constants defined that contain colors to use. They are:
- **BASIC_COLORS**: dict[str, ColorTuple]<br>
  Dict of color tuples, containing only the most basic colors.
- **GENERAL_COLORS**: dict[str, ColorTuple]<br>
  Dict of color tuples, containing general color names.
- **SKIN_TONE_COLORS**: dict[str, ColorTuple]<br>
  Dict of color tuples, containing skin tone color names.
- **SKIN_TONE_GRADIENT**: PIL.Image.Image<br>
  Image containing many different skin tones to pick from.
"""

import logging
import numpy as np
from skimage import color
import os
from pathlib import Path
from PIL import Image
from typing import Any, TypeVar, Union
import yaml

import src.Directories as Directories


_logger = logging.getLogger(__name__)
_rng = np.random.default_rng()


_Number = Union[int, float, np.number]
ColorTuple = tuple[_Number, _Number, _Number]
"""Type that describes a triplet of color values, for RGB, HSL, XYZ, and CIE-Lab color spaces."""
ColorOrImage = TypeVar("ColorOrImage", ColorTuple, np.ndarray)
"""Type that is either a ColorTuple or image array."""


def to_pil_color_tuple(color_tup: ColorTuple) -> tuple[int, int, int]:
    """Convert ColorTuple into a guaranteed all-int tuple for Pillow to be happy in type checking.

    Parameters
    ----------
    color_tup : ColorTuple
        color tuple to convert

    Returns
    -------
    tuple[int, int, int]
        all-int tuple
    """
    return (int(color_tup[0]), int(color_tup[1]), int(color_tup[2]))


def hex2rgb(hex_val: str) -> ColorTuple:
    """Convert a color in hex values to an RGB color tuple.

    Parameters
    ----------
    hex_val : str
        hex color in format #RRGGBB

    Returns
    -------
    ColorTuple
        3-tuple of colors in RGB, in interval [0, 255]
    """
    hex_val = hex_val.replace("#", "")
    r = int(hex_val[0:2], 16)
    g = int(hex_val[2:4], 16)
    b = int(hex_val[4:6], 16)
    return (r, g, b)


def rgb2hex(rgb: ColorTuple) -> str:
    """Convert an RGB color tuple to hex values.

    Parameters
    ----------
    rgb : ColorTuple
        3-tuple of colors in RGB, in interval [0, 255]

    Returns
    -------
    str
        hex color in format #RRGGBB
    """
    return "#" + "".join(hex(int(np.clip(color, 0, 255))).replace("0x", "").zfill(2) for color in rgb)


def hsv2hsl(hsv: np.ndarray) -> np.ndarray:
    """Convert HSV image to HSL image.

    Parameters
    ----------
    hsv : np.ndarray
        HSV color or image, all values in interval [0,1]

    Returns
    -------
    np.ndarray
        HSL color or image, all values in interval [0,1]
    """
    h = hsv[..., 0]
    s = hsv[..., 1]
    v = hsv[..., 2]
    l = v * (1 - s / 2)
    s_new = np.zeros(h.shape)
    l_in_0_1_open = np.logical_and(l != 0, l != 1)
    s_new[l_in_0_1_open] = (v[l_in_0_1_open] - l[l_in_0_1_open]) / np.minimum(l[l_in_0_1_open], 1 - l[l_in_0_1_open])
    if hsv.ndim == 1:
        return np.hstack((h, s_new, l))
    else:
        return np.dstack((h, s_new, l))


def hsl2hsv(hsl: np.ndarray) -> np.ndarray:
    """Convert HSL image to HSV image.

    Parameters
    ----------
    hsl : np.ndarray
        HSL color or image, all values in interval [0,1]

    Returns
    -------
    np.ndarray
        HSV color or image, all values in interval [0,1]
    """
    h = hsl[..., 0]
    s = hsl[..., 1]
    l = hsl[..., 2]
    v = l + s * np.minimum(l, 1 - l)
    s_new = np.zeros(h.shape)
    v_gt_0 = v != 0
    s_new[v_gt_0] = 2 * (1 - l[v_gt_0] / v[v_gt_0])
    if hsl.ndim == 1:
        return np.hstack((h, s_new, v))
    else:
        return np.dstack((h, s_new, v))


def rgb2hsl(rgb: np.ndarray) -> np.ndarray:
    """Convenience function to convert RGB image to HSL.

    Parameters
    ----------
    rgb : np.ndarray
        RGB color or image, all values in interval [0,255] with uint8 dtype

    Returns
    -------
    np.ndarray
        HSL color or image, all values in interval [0,1]
    """
    return hsv2hsl(color.rgb2hsv(rgb))


def hsl2rgb(hsl: np.ndarray) -> np.ndarray:
    """Convenience function to convert HSL image to RGB.

    Parameters
    ----------
    hsl : np.ndarray
        HSL color or image, all values in interval [0,1]

    Returns
    -------
    np.ndarray
        RGB color or image, all values in interval [0,255] with uint8 dtype
    """
    return (color.hsv2rgb(hsl2hsv(hsl)) * 255).astype(np.uint8)


def get_nearest_color_in_colors_list(rgb: ColorTuple, colors_dict: dict[str, ColorTuple]) -> tuple[str, ColorTuple]:
    """Get the closest color in the colors list to the input color.

    Parameters
    ----------
    rgb : ColorTuple
        RGB 3-tuple to find the closest color of
    colors_list : dict[str, ColorTuple]
        dict of color names to color tuples to reference

    Returns
    -------
    str
        name of the closest color
    ColorTuple
        color tuple of the closest color
    """
    # Get delta E between input color and all colors in colors list, then pick the minimum one
    def get_rgb_delta(color_tup1: ColorTuple, color_tup2: ColorTuple) -> _Number:
        return color.deltaE_cie76(
            color.rgb2lab(np.asarray(color_tup1, dtype=np.uint8)),
            color.rgb2lab(np.asarray(color_tup2, dtype=np.uint8)),
        )

    closest_color_name = min(colors_dict.keys(), key=lambda k: get_rgb_delta(colors_dict[k], rgb))
    return closest_color_name, colors_dict[closest_color_name]


def randomize_color(rgb: ColorTuple) -> ColorTuple:
    """Slightly randomize the hue, saturation, and lightness of the color.

    Parameters
    ----------
    rgb : ColorTuple
        3-tuple of colors in RGB, in interval [0, 255]

    Returns
    -------
    ColorTuple
        3-tuple of colors in RGB, in interval [0, 255] slightly randomized from input tuple `rgb`
    """
    h, s, l = rgb2hsl(np.asarray(rgb, dtype=np.uint8))
    # Randomize lightness more the closer it is to 50%.
    rand_light_factor = 1 - ((l - 0.5) / 0.5) ** 2
    new_hsl = np.asarray(
        (
            h + _rng.uniform(-0.025, 0.025),
            np.clip(s + _rng.normal(0, 0.025), 0.0, 1.0),
            np.clip(l + _rng.normal(0, 0.025) * rand_light_factor, 0.0, 1.0),
        ),
        dtype=np.float64,
    )
    new_rgb = hsl2rgb(new_hsl)
    return (new_rgb[0], new_rgb[1], new_rgb[2])


def brighten(rgb: ColorOrImage, amount: float = 0.1) -> ColorOrImage:
    """Brightens the color or image.

    Parameters
    ----------
    rgb : ColorOrImage
        3-tuple of colors or an image in RGB, values in interval [0, 255]
    amount : float, optional
        amount to increase lightness by, by default 10

    Returns
    -------
    ColorOrImage
        3-tuple of colors or an image in RGB, values in interval [0, 255] brightened from the input tuple `rgb`
    """
    hsl = rgb2hsl(np.asarray(rgb, dtype=np.uint8))
    h = hsl[..., 0]
    s = hsl[..., 1]
    l = hsl[..., 2]
    hsl_transform = (h, s, np.clip(l + amount, 0.0, 1.0))
    if isinstance(rgb, tuple):
        new_hsl = np.asarray(hsl_transform, dtype=np.float64)
    else:
        new_hsl = np.asarray(np.dstack(hsl_transform), dtype=np.float64)
    new_rgb = hsl2rgb(new_hsl)
    if isinstance(rgb, tuple):
        return (new_rgb[0], new_rgb[1], new_rgb[2])
    else:
        return new_rgb


def darken(rgb: ColorOrImage, amount: float = 0.05) -> ColorOrImage:
    """Darkens the color or image.

    Parameters
    ----------
    rgb : ColorOrImage
        3-tuple of colors or an image in RGB, values in interval [0, 255]
    amount : float, optional
        amount to decrease lightness by, by default 10

    Returns
    -------
    ColorOrImage
        3-tuple of colors or an image in RGB, values in interval [0, 255] darkened from input tuple `rgb`
    """
    return brighten(rgb, amount=-amount)


def complementary(rgb: ColorOrImage) -> ColorOrImage:
    """Returns the complementary color of the input color, or image where all colors are complementary.

    Parameters
    ----------
    rgb : ColorOrImage
        3-tuple of colors or an image in RGB, values in interval [0, 255]

    Returns
    -------
    ColorOrImage
        3-tuple of colors or an image in RGB, values in interval [0, 255] complementary to the input tuple `rgb`
    """
    hsl = rgb2hsl(np.asarray(rgb, dtype=np.uint8))
    h = hsl[..., 0]
    s = hsl[..., 1]
    l = hsl[..., 2]
    hsl_transform = ((h + 0.5) % 1.0, s, l)
    if isinstance(rgb, tuple):
        new_hsl = np.asarray(hsl_transform, dtype=np.float64)
    else:
        new_hsl = np.asarray(np.dstack(hsl_transform), dtype=np.float64)
    new_rgb = hsl2rgb(new_hsl)
    if isinstance(rgb, tuple):
        return (new_rgb[0], new_rgb[1], new_rgb[2])
    else:
        return new_rgb


def analogous(rgb: ColorOrImage, clockwise: bool = False) -> ColorOrImage:
    """Returns the analogous color of the input color (or image where all colors are analogous) in the counter-clockwise direction by default.

    Parameters
    ----------
    rgb : ColorOrImage
        3-tuple of colors or an image in RGB, values in interval [0, 255]
    clockwise : bool, optional
        whether the analogous color is calculated in clockwise direction or not, by default False

    Returns
    -------
    ColorOrImage
        3-tuple of colors or an image in RGB, values in interval [0, 255] analogous to the input tuple `rgb`
    """
    hsl = rgb2hsl(np.asarray(rgb, dtype=np.uint8))
    h = hsl[..., 0]
    s = hsl[..., 1]
    l = hsl[..., 2]
    angle_sign = -1 if clockwise else 1
    hsl_transform = ((h + 1.0 / 12.0 * angle_sign) % 1.0, s, l)
    if isinstance(rgb, tuple):
        new_hsl = np.asarray(hsl_transform, dtype=np.float64)
    else:
        new_hsl = np.asarray(np.dstack(hsl_transform), dtype=np.float64)
    new_rgb = hsl2rgb(new_hsl)
    if isinstance(rgb, tuple):
        return (new_rgb[0], new_rgb[1], new_rgb[2])
    else:
        return new_rgb


def analogous_ccw(rgb: ColorOrImage) -> ColorOrImage:
    """Returns the analogous color of the input color (or image where all colors are analogous) in the counter-clockwise direction.

    Parameters
    ----------
    rgb : ColorOrImage
        3-tuple of colors or an image in RGB, values in interval [0, 255]

    Returns
    -------
    ColorOrImage
        3-tuple of colors or an image in RGB, values in interval [0, 255] analogous to the input tuple `rgb` in the counter-clockwise direction
    """
    return analogous(rgb, clockwise=False)


def analogous_cw(rgb: ColorOrImage) -> ColorOrImage:
    """Returns the analogous color of the input color (or image where all colors are analogous) in the clockwise direction.

    Parameters
    ----------
    rgb : ColorOrImage
        3-tuple of colors or an image in RGB, values in interval [0, 255]

    Returns
    -------
    ColorOrImage
        3-tuple of colors or an image in RGB, values in interval [0, 255] analogous to the input tuple `rgb` in the clockwise direction
    """
    return analogous(rgb, clockwise=True)


def contrasting_text_color(rgb: ColorTuple) -> ColorTuple:
    """Get the color white or black, depending on whether it contrasts well with the input color.

    Parameters
    ----------
    rgb : ColorTuple
        3-tuple of colors to get contrasting color for

    Returns
    -------
    ColorTuple
        3-tuple of colors representing white or black
    """
    h, s, l = rgb2hsl(np.asarray(rgb, dtype=np.uint8))
    return (0, 0, 0) if l >= 0.5 else (255, 255, 255)


def get_colors_list(filename: Union[str, Path]) -> dict[str, ColorTuple]:
    """Reads a yaml file containing color names and their corresponding RGB triplets into a dict of color names to color tuples.

    The input yaml file will be in the following format:
    ```
    color name: '#RRGGBB'
    ```

    The output dict is similar to the yaml file, but with ColorTuple RGB triplets instead of the string hex values.

    Parameters
    ----------
    filename : str
        filename of the input text file

    Returns
    -------
    dict[str, ColorTuple]
        dictionary name of color names to color tuples from the yaml file
    """
    filepath = Path(filename)
    if filepath.is_file():
        colors_dict = yaml.safe_load(filepath.read_text())
        return {name: hex2rgb(value) for name, value in colors_dict.items()}
    else:
        _logger.warn("colors list not found. Loading a basic colors dict")
        return _BASIC_COLORS


# Module constants defined below

_BASIC_COLORS: dict[str, ColorTuple] = {
    "red": (255, 0, 0),
    "yellow": (255, 255, 0),
    "green": (0, 255, 0),
    "cyan": (0, 255, 255),
    "blue": (0, 0, 255),
    "magenta": (255, 0, 255),
    "black": (0, 0, 0),
    "white": (255, 255, 255),
}
_GENERAL_COLORS = get_colors_list(Directories.DATA_DIR / "colors.general.yml")
_SKIN_TONE_COLORS = get_colors_list(Directories.DATA_DIR / "colors.skintones.yml")
if os.path.exists((_skin_tone_gradient_file := Directories.DATA_DIR / "colors.skintones.gradient.png")):
    _SKIN_TONE_GRADIENT = Image.open(_skin_tone_gradient_file)
else:
    _logger.warn("skin tones gradient not found. Loading a dummy image")
    _SKIN_TONE_GRADIENT = Image.new("RGB", (1, 1), (128, 128, 128))


def __getattr__(name: str) -> Any:
    attrs = {
        "BASIC_COLORS": _BASIC_COLORS,
        "GENERAL_COLORS": _GENERAL_COLORS,
        "SKIN_TONE_COLORS": _SKIN_TONE_COLORS,
        "SKIN_TONE_GRADIENT": _SKIN_TONE_GRADIENT,
    }
    if name in attrs:
        return attrs[name]
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
