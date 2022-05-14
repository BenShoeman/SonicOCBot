"""Utilities for reading and manipulating images."""

from math import sqrt
from PIL import Image
import random

from .ColorUtil import ColorTuple, get_rgb_delta, multiply_colors


def get_random_color_from_image(img: Image.Image) -> ColorTuple:
    """Get a random color from the input image.

    Parameters
    ----------
    img : Image.Image
        Pillow image to get a random color from

    Returns
    -------
    ColorTuple
        3-tuple of colors in RGB
    """
    img = img.convert("RGB")
    width, height = img.size
    random_x = random.randrange(0, width)
    random_y = random.randrange(0, height)
    r, g, b = img.getpixel((random_x, random_y))
    return (float(r), float(g), float(b))


def multiply_floodfill(img: Image.Image, xy: tuple[int, int], color: tuple[int, int, int], threshold: int = 16) -> None:
    """Flood fill a region in the image by using multiply blending.

    Parameters
    ----------
    img : Image.Image
        image to flood fill
    xy : tuple[int, int]
        (x,y) coordinate to flood fill
    color : tuple[int, int, int]
        RGB 3-tuple containing color to fill with
    threshold : int, optional
        tolerance with which similar colors to initial (x,y) point can also be filled, by default 16
    """
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    img_rgb = img.convert("RGB")
    width, height = img_rgb.size

    # Return if xy point can't be filled in
    if xy[0] < 0 or xy[0] >= width or xy[1] < 0 or xy[1] >= height:
        print(f"Error: can't flood fill. xy-coordinates of {xy} not contained in image of dimensions {width}x{height}")
        return

    init_r, init_g, init_b = img_rgb.getpixel(xy)
    initial_color = (float(init_r), float(init_g), float(init_b))
    initial_alpha = img.getpixel(xy)[3]
    fill_pixels = set()
    explored_pixels = set()
    explored_pixels.add(xy)
    next_pixels = [xy]

    while next_pixels:
        curr_xy = next_pixels.pop(0)
        fill_pixels.add(curr_xy)
        x, y = curr_xy
        radius = 1
        nearby_pixels = [
            ij
            for i in range(x - radius, x + radius + 1)
            for j in range(y - radius, y + radius + 1)
            if (ij := (i, j)) not in explored_pixels and 0 <= i < width and 0 <= j < height
        ]
        for ij in nearby_pixels:
            explored_pixels.add(ij)
            # Recursively find neighboring pixels & mark to fill those within the threshold too
            ij_r, ij_g, ij_b = img_rgb.getpixel(ij)
            ij_color = (float(ij_r), float(ij_g), float(ij_b))
            if abs(initial_alpha - img.getpixel(ij)[3]) <= threshold and sqrt(get_rgb_delta(initial_color, ij_color)) <= threshold:
                next_pixels.append(ij)

    for x, y in fill_pixels:
        curr_r, curr_g, curr_b = img_rgb.getpixel((x, y))
        current_color = (float(curr_r), float(curr_g), float(curr_b))
        current_alpha = img.getpixel((x, y))[3]
        new_color = tuple(int(c) for c in multiply_colors(color, current_color))
        img.putpixel((x, y), new_color + (current_alpha,))
