"""Utilities for reading and manipulating colors.

This module has 4 constants defined that contain colors to use. They are:
- **BASIC_COLORS**: list[ColorDict]<br>
  List of color dictionaries, containing only the most basic colors and their RGB 3-tuples.
- **GENERAL_COLORS**: list[ColorDict]<br>
  List of color dictionaries, containing general color names and their RGB 3-tuples.
- **SKIN_TONE_COLORS**: list[ColorDict]<br>
  List of color dictionaries, containing skin tone color names and their RGB 3-tuples.
- **SKIN_TONE_GRADIENT**: PIL.Image.Image<br>
  Image containing many different skin tones to pick from.
"""

import numpy as np
from skimage import color
import os
from PIL import Image
from typing import Any, TypedDict, TypeVar, Union

import src.Directories as Directories


_rng = np.random.default_rng()


_Number = Union[int, float, np.number]
ColorTuple = tuple[_Number, _Number, _Number]
"""Type that describes a triplet of color values, for RGB, HSL, XYZ, and CIE-Lab color spaces."""
ColorOrImage = TypeVar("ColorOrImage", ColorTuple, np.ndarray)
"""Type that is either a ColorTuple or image array."""


class ColorDict(TypedDict):
    """Dictionary type containing color names and their corresponding RGB 3-tuples."""

    name: str
    color: ColorTuple


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


def get_nearest_color_in_colors_list(rgb: ColorTuple, colors_list: list[ColorDict]) -> ColorDict:
    """Get the closest color in the colors list to the input color.

    Parameters
    ----------
    rgb : ColorTuple
        RGB 3-tuple to find the closest color of
    colors_list : list[ColorDict]
        list of `ColorDict` dictionaries with colors to reference

    Returns
    -------
    ColorDict
        `ColorDict` of the closest color
    """
    # Get delta E between input color and all colors in colors list, then pick the minimum one
    def get_rgb_delta(color_tup1: ColorTuple, color_tup2: ColorTuple) -> _Number:
        return color.deltaE_cie76(
            color.rgb2lab(np.asarray(color_tup1, dtype=np.uint8)),
            color.rgb2lab(np.asarray(color_tup2, dtype=np.uint8)),
        )

    return min(colors_list, key=lambda color_dict: get_rgb_delta(color_dict["color"], rgb))


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


def get_colors_list(filename: Union[str, os.PathLike]) -> list[ColorDict]:
    """Reads a text file containing RGB triplets and their corresponding names into a list.

    The input list will be in the following format:
    ```
    RRR,GGG,BBB:color name
    ```

    For example, below could be a color list:
    ```
    255,  0,  0:red
      0,255,255:cyan
    ```

    The output list contains dictionaries with keys `"name"` and `"color"` for each color.
    See `ColorDict` type for more information on this.

    Parameters
    ----------
    filename : str
        filename of the input text file

    Returns
    -------
    list[ColorDict]
        list of dictionaries containing name and color information for each color
    """

    try:
        with open(filename, "r") as f:
            colorlist: list[list[Any]] = [line.strip().split(":") for line in f.readlines()]
            # Convert the first half of each line into color triplets
            for i in range(len(colorlist)):
                colorlist[i][0] = tuple(np.clip(int(value.strip()), 0, 255) for value in colorlist[i][0].split(","))
            # Finally, create the list of ColorDicts
            colors = [ColorDict(name=color_name, color=color_tuple) for color_tuple, color_name in colorlist]
    except FileNotFoundError:
        print("Error: colors list not found. Loading a basic colors list")
        colors = _BASIC_COLORS
    return colors


# Module constants defined below

_BASIC_COLORS = [
    ColorDict(name="red", color=(255, 0, 0)),
    ColorDict(name="yellow", color=(255, 255, 0)),
    ColorDict(name="green", color=(0, 255, 0)),
    ColorDict(name="cyan", color=(0, 255, 255)),
    ColorDict(name="blue", color=(0, 0, 255)),
    ColorDict(name="magenta", color=(255, 0, 255)),
    ColorDict(name="black", color=(0, 0, 0)),
    ColorDict(name="white", color=(255, 255, 255)),
]
_GENERAL_COLORS = get_colors_list(Directories.DATA_DIR / "colors.general.txt")
_SKIN_TONE_COLORS = get_colors_list(Directories.DATA_DIR / "colors.skintones.txt")
if os.path.exists((_skin_tone_gradient_file := Directories.DATA_DIR / "colors.skintones.gradient.png")):
    _SKIN_TONE_GRADIENT = Image.open(_skin_tone_gradient_file)
else:
    print("Error: skin tones gradient not found. Loading a dummy image")
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
