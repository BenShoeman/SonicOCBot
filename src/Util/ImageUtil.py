"""Utilities for reading and manipulating images."""

from base64 import b64encode
from io import BytesIO
import numpy as np
from PIL import Image
import random
from scipy.ndimage import label
from typing import Callable, Optional, TypeVar, Union

from .ColorUtil import ColorTuple


ImageLike = TypeVar("ImageLike", Image.Image, np.ndarray)
"""Image-like; i.e., a PIL image or numpy image array."""


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
    return img.getpixel((random_x, random_y))


def tile_image_to_size(img: ImageLike, size: tuple[int, int]) -> ImageLike:
    """Tile the input image to a given size.

    Parameters
    ----------
    img : ImageLike (Image.Image or np.ndarray)
        image to tile
    size : tuple[int, int]
        size to tile to

    Returns
    -------
    ImageLike
        a new PIL image or numpy array of the tiled image, same type as input
    """
    img_arr = np.array(img)
    w_tgt, h_tgt = size
    h_fill, w_fill = img_arr.shape[:2]
    # Tile so that the fill pattern is larger than the image we are filling
    extra_dims = (1,) * (img_arr.ndim - 2)
    if h_fill < h_tgt:
        img_arr = np.tile(img_arr, (int(np.ceil(h_tgt / h_fill)), 1) + extra_dims)
    if w_fill < w_tgt:
        img_arr = np.tile(img_arr, (1, int(np.ceil(w_tgt / w_fill))) + extra_dims)
    # Then return cropped and tiled image
    img_arr = img_arr[:h_tgt, :w_tgt, :]
    return Image.fromarray(img_arr) if isinstance(img, Image.Image) else img_arr


def floodfill(
    img: ImageLike,
    xy: tuple[int, int],
    fill: Union[ColorTuple, Image.Image, np.ndarray],
    threshold: int = 16,
    method: Optional[Callable[[np.ndarray, np.ndarray], np.ndarray]] = None,
    in_place: bool = False,
) -> ImageLike:
    """Flood fill a region in the image, optionally with a custom fill method.

    Note that the image must be an RGB or RGBA image. Also, this method only considers RGB; alpha is ignored.

    Parameters
    ----------
    img : ImageLike
        image or image array to flood fill; MUST be RGB or RGBA
    xy : tuple[int, int]
        (x,y) coordinate to flood fill
    fill : Union[ColorTuple, Image.Image, np.ndarray]
        what to fill in the space; either a RGB 3-tuple containing color to fill, or image with pattern to fill;
        note that if it's an image, the alpha channel will be ignored
    threshold : int, optional
        tolerance with which similar colors to initial (x,y) point can also be filled, by default 16
    method: Optional[Callable[[np.ndarray, np.ndarray], np.ndarray]], optional
        method to fill using, in form `lambda orig, new: ...`;
        in the lambda function, `orig` and `new` are numpy arrays containing original image data and new color to fill with;
        if omitted, this will just do a regular floodfill
    in_place: boolean, optional
        only takes effect if `img` is type np.ndarray; if True, then does the operation in place, by default False

    Returns
    -------
    ImageLike
        the modified PIL image or numpy array, same type as input
    """
    # Just use the target color to fill if method is undefined
    if not method:
        method = lambda orig, new: new

    if in_place:
        img_arr = np.asarray(img)
    else:
        img_arr = np.array(img)
    x, y = xy
    img_rgb = img_arr[:, :, :3].astype(np.int16)

    # Make sure pattern is the same size as the image for masking later
    if isinstance(fill, (Image.Image, np.ndarray)):
        h_img, w_img = img_arr.shape[:2]
        fill_arr = np.asarray(tile_image_to_size(np.asarray(fill), (w_img, h_img)))
        # Only use RGB channels for pattern fill
        fill_arr = fill_arr[:, :, :3]

    init_color = img_rgb[y, x]

    # Find where difference between initial color and all colors in image is less than threshold for all channels
    diffs = np.abs(img_rgb - init_color)
    match_regions = np.logical_and(np.logical_and(diffs[:, :, 0] <= threshold, diffs[:, :, 1] <= threshold), diffs[:, :, 2] <= threshold)
    # match_regions = np.sum(np.abs(img_rgb - init_color), axis=2) <= (threshold * 3)
    # Then, get contiguous region starting at initial color using scipy.ndimage.label
    labels, _ = label(match_regions)
    # If fill is just a color, convert it to numpy array; else, get where pattern overlaps image
    mask = labels == labels[y, x]
    if isinstance(fill, tuple):
        tgt_fill = np.asarray(fill)
    else:
        tgt_fill = fill_arr[mask]
    img_rgb[mask] = method(img_rgb[mask], tgt_fill)
    img_arr[:, :, :3] = img_rgb

    # Convert back to PIL image if PIL image was inputted
    if isinstance(img, Image.Image):
        img = Image.fromarray(img_arr)
    return img


def multiply_floodfill(
    img: ImageLike,
    xy: tuple[int, int],
    fill: Union[ColorTuple, Image.Image, np.ndarray],
    threshold: int = 16,
    in_place: bool = False,
) -> ImageLike:
    """Flood fill a region in the image by using multiply blending using `ImageUtil.floodfill`.

    Parameters
    ----------
    img : ImageLike
        image or image array to flood fill
    xy : tuple[int, int]
        (x,y) coordinate to flood fill
    fill : Union[ColorTuple, Image.Image, np.ndarray]
        what to fill in the space; either a RGB 3-tuple containing color to fill, or image with pattern to fill
    threshold : int, optional
        tolerance with which similar colors to initial (x,y) point can also be filled, by default 16
    in_place: boolean, optional
        only takes effect if `img` is type np.ndarray; if True, then does the operation in place, by default False

    Returns
    -------
    ImageLike
        the modified PIL image or numpy array, same type as input
    """
    return floodfill(img, xy, fill, threshold, method=lambda orig, new: orig * new // 255, in_place=in_place)


def image_to_data_url(img: Image.Image) -> str:
    """Create a data URL from the inputted image.

    Parameters
    ----------
    img : Image.Image
        PIL image to convert to a data URL (as a PNG)

    Returns
    -------
    str
        data URL of the image
    """
    with BytesIO() as f:
        img.save(f, format="PNG")
        f.seek(0)
        b64_contents = b64encode(f.read()).decode("utf-8")
    return f"data:image/png;base64,{b64_contents}"
