import random
import re
import os
from PIL import Image
from typing import Any, TypedDict, Union

import src.Directories as Directories

ColorTuple = tuple[Union[int, float], Union[int, float], Union[int, float]]


class ColorDict(TypedDict):
    """Dictionary containing color names and their corresponding RGB 3-tuples"""

    name: str
    color: ColorTuple


def _clamp(n: Union[int, float], min_val: Union[int, float], max_val: Union[int, float]) -> Union[int, float]:
    return min_val if n < min_val else (max_val if n > max_val else n)


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
                colorlist[i][0] = tuple(_clamp(float(value.strip()), 0, 255) for value in colorlist[i][0].split(","))
            # Finally, create the list of ColorDicts
            colors = [ColorDict(name=color_name, color=color_tuple) for color_tuple, color_name in colorlist]
    except FileNotFoundError:
        print("Error: colors list not found. Loading a basic colors list")
        colors = BASIC_COLORS
    return colors


BASIC_COLORS = [
    ColorDict(name="red", color=(255.0, 0.0, 0.0)),
    ColorDict(name="yellow", color=(255.0, 255.0, 0.0)),
    ColorDict(name="green", color=(0.0, 255.0, 0.0)),
    ColorDict(name="cyan", color=(0.0, 255.0, 255.0)),
    ColorDict(name="blue", color=(0.0, 0.0, 255.0)),
    ColorDict(name="magenta", color=(255.0, 0.0, 255.0)),
    ColorDict(name="black", color=(0.0, 0.0, 0.0)),
    ColorDict(name="white", color=(255.0, 255.0, 255.0)),
]
"""List of color dictionaries, containing only the most basic colors and their RGB 3-tuples"""

GENERAL_COLORS = get_colors_list(os.path.join(Directories.DATA_DIR, "colors.general.txt"))
"""List of color dictionaries, containing general color names and their RGB 3-tuples"""

SKIN_TONE_COLORS = get_colors_list(os.path.join(Directories.DATA_DIR, "colors.skintones.txt"))
"""List of color dictionaries, containing skin tone color names and their RGB 3-tuples"""

if os.path.exists((_skin_tone_gradient_file := os.path.join(Directories.DATA_DIR, "colors.skintones.gradient.png"))):
    SKIN_TONE_GRADIENT = Image.open(_skin_tone_gradient_file)
else:
    print("Error: skin tones gradient not found. Loading a dummy image")
    SKIN_TONE_GRADIENT = Image.new("RGB", (1, 1), (128, 128, 128))


def hex_to_rgb(hex_val: str) -> ColorTuple:
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


def rgb_to_hex(rgb: ColorTuple) -> str:
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
    return "#" + "".join(hex(int(_clamp(color, 0, 255))).replace("0x", "").zfill(2) for color in rgb)


def rgb_to_hsl(rgb: ColorTuple) -> ColorTuple:
    """Convert an RGB color tuple into an HSL color tuple.

    Parameters
    ----------
    rgb : ColorTuple
        3-tuple of colors in RGB, in interval [0, 255]

    Returns
    -------
    ColorTuple
        3-tuple of colors in HSL, where hue is in [0, 360) and saturation/lightness are in [0, 100]
    """

    # Get RGB values and put them in range 0..1
    r = rgb[0] / 255.0
    g = rgb[1] / 255.0
    b = rgb[2] / 255.0
    cmax = max(r, g, b)
    cmin = min(r, g, b)
    delta = cmax - cmin

    l = (cmax + cmin) / 2
    if delta == 0:
        return (0, 0, round(l * 100, 2))

    s = delta / (1 - abs(2 * l - 1))

    if cmax == r:
        h = 60 * (((g - b) / delta) % 6)
    elif cmax == g:
        h = 60 * (((b - r) / delta) + 2)
    else:
        h = 60 * (((r - g) / delta) + 4)

    # Return HSL values in the range [0,360) for hue, [0,100] for saturation/lightness
    h_rounded = round(h, 2)
    s_normed = round(s * 100, 2)
    l_normed = round(l * 100, 2)
    return (h_rounded, s_normed, l_normed)


def hsl_to_rgb(hsl: ColorTuple) -> ColorTuple:
    """Convert an HSL color tuple into an RGB color tuple.

    Parameters
    ----------
    hsl : ColorTuple
        3-tuple of colors in HSL, where hue is in [0, 360) and saturation/lightness are in [0, 100]

    Returns
    -------
    ColorTuple
        3-tuple of colors in RGB, in interval [0, 255]
    """

    # Get saturation and lightness in range [0,1]
    h = float(hsl[0])
    s = hsl[1] / 100.0
    l = hsl[2] / 100.0

    c = (1 - abs(2 * l - 1)) * s
    hh = float(h) / 60
    x = c * (1 - abs(hh % 2 - 1))
    m = l - c / 2

    r = 0.0
    g = 0.0
    b = 0.0
    if hh >= 5:
        r = c
        b = x
    elif hh >= 4:
        r = x
        b = c
    elif hh >= 3:
        g = x
        b = c
    elif hh >= 2:
        g = c
        b = x
    elif hh >= 1:
        r = x
        g = c
    else:
        r = c
        g = x

    # Return RGB values in the range [0,255]
    r_standard = float(round((r + m) * 255))
    g_standard = float(round((g + m) * 255))
    b_standard = float(round((b + m) * 255))
    return (r_standard, g_standard, b_standard)


def rgb_to_xyz(rgb: ColorTuple) -> ColorTuple:
    """Convert an RGB color tuple to an XYZ color tuple.

    Parameters
    ----------
    rgb : ColorTuple
        3-tuple of colors in RGB, in interval [0, 255]

    Returns
    -------
    ColorTuple
        3-tuple of colors in XYZ, with the following ranges coming from an sRGB color:
        - X in [0, 95.047]
        - Y in [0, 100.000]
        - Z in [0, 108.883]
    """

    standard_r, standard_g, standard_b = rgb

    r = standard_r / 255
    g = standard_g / 255
    b = standard_b / 255

    if r > 0.04045:
        r = ((r + 0.055) / 1.055) ** 2.4
    else:
        r = r / 12.92
    if g > 0.04045:
        g = ((g + 0.055) / 1.055) ** 2.4
    else:
        g = g / 12.92
    if b > 0.04045:
        b = ((b + 0.055) / 1.055) ** 2.4
    else:
        b = b / 12.92

    r = r * 100
    g = g * 100
    b = b * 100

    x = r * 0.4124 + g * 0.3576 + b * 0.1805
    y = r * 0.2126 + g * 0.7152 + b * 0.0722
    z = r * 0.0193 + g * 0.1192 + b * 0.9505
    return (x, y, z)


def xyz_to_lab(xyz: ColorTuple) -> ColorTuple:
    """Convert an XYZ color tuple into a CIE-Lab color tuple.

    Parameters
    ----------
    xyz : ColorTuple
        3-tuple of colors in XYZ, with the following ranges coming from an sRGB color:
        - X in [0, 95.047]
        - Y in [0, 100.000]
        - Z in [0, 108.883]

    Returns
    -------
    ColorTuple
        3-tuple of colors in CIE-Lab, normally with the following ranges coming from an sRGB color:
        - L in [0, 100]
        - a in [-128, 127]
        - b in [-128, 127]
    """

    x_orig, y_orig, z_orig = xyz

    x = x_orig / 95.047
    y = y_orig / 100
    z = z_orig / 108.883

    if x > 0.008856:
        x = x ** (1 / 3)
    else:
        x = (7.787 * x) + (16 / 116)
    if y > 0.008856:
        y = y ** (1 / 3)
    else:
        y = (7.787 * y) + (16 / 116)
    if z > 0.008856:
        z = z ** (1 / 3)
    else:
        z = (7.787 * z) + (16 / 116)

    L = (116 * y) - 16
    a = 500 * (x - y)
    b = 200 * (y - z)
    return (L, a, b)


def lab_to_xyz(lab: ColorTuple) -> ColorTuple:
    """Convert a CIE-Lab color tuple into an XYZ color tuple.

    Parameters
    ----------
    lab : ColorTuple
        3-tuple of colors in CIE-Lab, normally with the following ranges coming from an sRGB color:
        - L in [0, 100]
        - a in [-128, 127]
        - b in [-128, 127]

    Returns
    -------
    ColorTuple
        3-tuple of colors in XYZ, with the following ranges coming from an sRGB color:
        - X in [0, 95.047]
        - Y in [0, 100.000]
        - Z in [0, 108.883]
    """

    L, a, b = lab

    y = (L + 16) / 116
    x = a / 500 + y
    z = y - b / 200

    if y**3 > 0.008856:
        y = y**3
    else:
        y = (y - 16 / 116) / 7.787
    if x**3 > 0.008856:
        x = x**3
    else:
        x = (x - 16 / 116) / 7.787
    if z**3 > 0.008856:
        z = z**3
    else:
        z = (z - 16 / 116) / 7.787

    x = x * 95.047
    y = y * 100
    z = z * 108.883
    return (x, y, z)


def xyz_to_rgb(xyz: ColorTuple) -> ColorTuple:
    """Convert an XYZ color tuple into an RGB color tuple.

    Parameters
    ----------
    xyz : ColorTuple
        3-tuple of colors in XYZ, with the following ranges coming from an sRGB color:
        - X in [0, 95.047]
        - Y in [0, 100.000]
        - Z in [0, 108.883]

    Returns
    -------
    ColorTuple
        3-tuple of colors in RGB, in interval [0, 255]
    """

    x_orig, y_orig, z_orig = xyz

    x = x_orig / 100
    y = y_orig / 100
    z = z_orig / 100

    r = x * 3.2406 + y * -1.5372 + z * -0.4986
    g = x * -0.9689 + y * 1.8758 + z * 0.0415
    b = x * 0.0557 + y * -0.2040 + z * 1.0570

    if r > 0.0031308:
        r = 1.055 * (r ** (1 / 2.4)) - 0.055
    else:
        r = 12.92 * r
    if g > 0.0031308:
        g = 1.055 * (g ** (1 / 2.4)) - 0.055
    else:
        g = 12.92 * g
    if b > 0.0031308:
        b = 1.055 * (b ** (1 / 2.4)) - 0.055
    else:
        b = 12.92 * b

    standard_r = r * 255
    standard_g = g * 255
    standard_b = b * 255
    return (standard_r, standard_g, standard_b)


def rgb_to_lab(rgb: ColorTuple) -> ColorTuple:
    """Convenience function to convert an RGB color tuple into a CIE-Lab color tuple, using XYZ as an intermediate step.

    Parameters
    ----------
    rgb : ColorTuple
        3-tuple of colors in RGB

    Returns
    -------
    ColorTuple
        3-tuple of colors in CIE-Lab
    """
    return xyz_to_lab(rgb_to_xyz(rgb))


def lab_to_rgb(lab: ColorTuple) -> ColorTuple:
    """Convenience function to convert a CIE-Lab color tuple into an RGB color tuple, using XYZ as an intermediate step.

    Parameters
    ----------
    rgb : ColorTuple
        3-tuple of colors in CIE-Lab

    Returns
    -------
    ColorTuple
        3-tuple of colors in RGB
    """
    return xyz_to_rgb(lab_to_xyz(lab))


def get_rgb_delta(rgb1: ColorTuple, rgb2: ColorTuple) -> float:
    """Get distance between RGB colors in CIE-Lab color space, for comparing which colors are close to each other.

    Parameters
    ----------
    rgb1 : ColorTuple
        first RGB 3-tuple to compare
    rgb2 : ColorTuple
        second RGB 3-tuple to compare

    Returns
    -------
    float
        delta between the two RGB 3-tuples
    """
    L1, a1, b1 = rgb_to_lab(rgb1)
    L2, a2, b2 = rgb_to_lab(rgb2)
    delta_L = L2 - L1
    delta_a = a2 - a1
    delta_b = b2 - b1
    return delta_L * delta_L + delta_a * delta_a + delta_b * delta_b


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
    h, s, l = rgb_to_hsl(rgb)
    # Randomize lightness more the closer it is to 50%.
    rand_light_factor = 1 - ((l - 50) / 50) ** 2
    new_hsl = (h + random.random() * 16 - 8, _clamp(s + random.gauss(0, 2.5), 0, 100), _clamp(l + random.gauss(0, 2.5) * rand_light_factor, 0, 100))
    return hsl_to_rgb(new_hsl)


def brighten_color(rgb: ColorTuple, amount: float = 10) -> ColorTuple:
    """Brightens the color.

    Parameters
    ----------
    rgb : ColorTuple
        3-tuple of colors in RGB, in interval [0, 255]
    amount : float, optional
        amount to increase lightness by, by default 10

    Returns
    -------
    ColorTuple
        3-tuple of colors in RGB, in interval [0, 255] brightened from the input tuple `rgb`
    """
    h, s, l = rgb_to_hsl(rgb)
    new_hsl = (h, s, _clamp(l + amount, 0, 100))
    return hsl_to_rgb(new_hsl)


def darken_color(rgb: ColorTuple, amount: float = 10) -> ColorTuple:
    """Darkens the color.

    Parameters
    ----------
    rgb : ColorTuple
        3-tuple of colors in RGB, in interval [0, 255]
    amount : float, optional
        amount to decrease lightness by, by default 10

    Returns
    -------
    ColorTuple
        3-tuple of colors in RGB, in interval [0, 255] darkened from input tuple `rgb`
    """
    return brighten_color(rgb, amount=-amount)


def complementary_color(rgb: ColorTuple) -> ColorTuple:
    """Returns the complementary color of the input color.

    Parameters
    ----------
    rgb : ColorTuple
        3-tuple of colors in RGB, in interval [0, 255]

    Returns
    -------
    ColorTuple
        3-tuple of colors in RGB, in interval [0, 255] complementary to the input tuple `rgb`
    """
    h, s, l = rgb_to_hsl(rgb)
    new_hsl = ((h + 180) % 360, s, l)
    return hsl_to_rgb(new_hsl)


def analogous_color(rgb: ColorTuple, clockwise: bool = False) -> ColorTuple:
    """Returns the analogous color of the input color in the counter-clockwise direction by default.

    Parameters
    ----------
    rgb : ColorTuple
        3-tuple of colors in RGB, in interval [0, 255]
    clockwise : bool, optional
        whether the analogous color is calculated in clockwise direction or not, by default False

    Returns
    -------
    ColorTuple
        3-tuple of colors in RGB, in interval [0, 255] analogous to the input tuple `rgb`
    """
    h, s, l = rgb_to_hsl(rgb)
    angle_sign = -1 if clockwise else 1
    new_hsl = ((h + 30 * angle_sign) % 360, s, l)
    return hsl_to_rgb(new_hsl)


def analogous_ccw_color(rgb: ColorTuple) -> ColorTuple:
    """Returns the analogous color of the input color in the counter-clockwise direction.

    Parameters
    ----------
    rgb : ColorTuple
        3-tuple of colors in RGB, in interval [0, 255]

    Returns
    -------
    ColorTuple
        3-tuple of colors in RGB, in interval [0, 255] analogous to the input tuple `rgb` in the counter-clockwise direction
    """
    return analogous_color(rgb, clockwise=False)


def analogous_cw_color(rgb: ColorTuple) -> ColorTuple:
    """Returns the analogous color of the input color in the clockwise direction.

    Parameters
    ----------
    rgb : ColorTuple
        3-tuple of colors in RGB, in interval [0, 255]

    Returns
    -------
    ColorTuple
        3-tuple of colors in RGB, in interval [0, 255] analogous to the input tuple `rgb` in the clockwise direction
    """
    return analogous_color(rgb, clockwise=True)


def multiply_colors(rgb1: ColorTuple, rgb2: ColorTuple) -> tuple:
    """Multiply blend the two colors.

    Parameters
    ----------
    rgb1 : ColorTuple
        first color to blend
    rgb2 : ColorTuple
        second color to blend

    Returns
    -------
    ColorTuple
        blended color
    """
    return tuple(color1 * color2 / 255 for color1, color2 in zip(rgb1, rgb2))
