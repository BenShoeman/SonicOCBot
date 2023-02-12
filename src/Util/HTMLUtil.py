"""Utilities to convert HTML and Markdown documents to images."""

from html2image import Html2Image
from html2text import HTML2Text
from jinja2 import Environment, FileSystemLoader
import os
from pathlib import Path
from PIL import Image
import pycmarkgfm as gfm
import re
import tempfile
from typing import Any, Optional, Union

import src.Directories as Directories

CSSDict = dict[str, Union[dict[str, str], list[dict[str, str]]]]
"""Dictionary type containing CSS attributes and values."""


def fill_jinja_template(template_file: Union[str, Path], **kwargs: Any) -> str:
    """Return a filled Jinja template using the keyword arguments; easy wrapper around Jinja template rendering.

    This does support template inheritance but only when the inherited template is in the same directory as the template file.

    Parameters
    ----------
    template_file : PathLike
        Jinja template to fill out

    Other Parameters
    ----------------
    **kwargs : dict
        parts of the Jinja template to fill out, just like jinja2 `render` method

    Returns
    -------
    str
        Jinja template filled out with the kwargs
    """
    template_path = Path(template_file)
    env = Environment(loader=FileSystemLoader((Directories.TEMPLATES_DIR, template_path.parent)))
    return env.get_template(template_path.name).render(**kwargs)


def html_to_image(
    html_str: str,
    css: Union[str, CSSDict] = "",
    width: int = 1000,
    height: Optional[int] = None,
    crop_transparency: bool = True,
) -> Image.Image:
    """Convert HTML to an image using `html2image`.

    If `html2image` is not detecting the Chrome/Chromium path, pass it in using the `CHROME_BIN` environment variable.

    Parameters
    ----------
    html_str : str
        HTML string to convert
    css : Union[str, CSSDict], optional
        CSS string to use for styling, or dict containing selectors as keys and attribute subdicts, by default ""
    width : int, optional
        width of the exported image, by default 1000
    height : int, optional
        height of the exported image, by default 5*width (intended to be cropped off later)
    crop_transparency : bool, optional
        whether to crop transparency, by default True

    Returns
    -------
    Image.Image
        HTML and CSS converted to an image
    """
    css_str = dict_to_css(css).strip() if isinstance(css, dict) else css
    # Add page size details to CSS
    height = height if height else width * 5
    css_str += f"@page {{ size: {width}px {height}px; margin: 0; }}\n"
    with tempfile.NamedTemporaryFile(suffix=".png") as f:
        f_path = Path(f.name)
        h2i = Html2Image(
            output_path=f_path.parent,
            browser_executable=os.getenv("CHROME_BIN"),
            custom_flags=["--default-background-color=0", "--hide-scrollbars", "--disable-gpu", *os.getenv("CHROME_ARGS", "").split()],
        )
        h2i.screenshot(html_str=html_str, css_str=css_str, save_as=f_path.name, size=(width, height))
        text_img = Image.open(f_path).convert("RGBA")
    # Resize image to match expected width if it doesn't match, for hidpi issues
    text_img_width, text_img_height = text_img.size
    resize_ratio = width / text_img_width
    text_img = text_img.resize((width, int(text_img_height * resize_ratio)))
    if crop_transparency:
        bbox = text_img.getbbox()
        text_img = text_img.crop(bbox)
    return text_img


def md_to_image(md_str: str, **kwargs: Any) -> Image.Image:
    """Convert Markdown to an image using `html_to_image`.

    Parameters
    ----------
    md_str : str
        MD string to convert

    Other Parameters
    ----------------
    **kwargs : dict
        The non-HTML arguments in `html_to_image`: css, width, height, crop_transparency

    Returns
    -------
    Image.Image
        MD and CSS converted to an image
    """
    html_str = f"<html><body>{gfm.gfm_to_html(md_str)}</body></html>"
    return html_to_image(html_str=html_str, **kwargs)


def md_to_plaintext(md_str: str) -> str:
    """Convert markdown to plain, unformatted text.

    Parameters
    ----------
    md_str : str
        MD string to convert

    Returns
    -------
    str
        plain unformatted text with no markdown elements
    """
    h2t = HTML2Text()
    h2t.ignore_links = True
    h2t.ignore_images = True
    h2t.body_width = 2147483647
    h2t.ul_item_mark = "-"
    h2t.emphasis_mark = ""
    h2t.strong_mark = ""
    # Do some adjustments to make it look better for plaintext
    html_str = re.sub(r"<(/?)h\d>", r"<\1p>", gfm.gfm_to_html(md_str))
    plaintext = re.sub(r"^\*\s+\*\s+\*$", "-----", h2t.handle(html_str), flags=re.MULTILINE)
    return plaintext


def dict_to_css(css_dict: CSSDict) -> str:
    """Convert the dictionary to a CSS string.

    Parameters
    ----------
    css_dict : dict
        CSS dict containing selectors as keys and attribute subdicts

    Returns
    -------
    str
        CSS string
    """
    css_str = ""
    for selector, attrs in css_dict.items():
        if isinstance(attrs, list):
            for attrs_dict in attrs:
                css_str += selector + " {"
                for attr, value in attrs_dict.items():
                    css_str += f"{attr}:{value};"
                css_str += "}\n"

        else:  # is a dict
            css_str += selector + " {"
            for attr, value in attrs.items():
                css_str += f"{attr}:{value};"
            css_str += "}\n"

    return css_str
