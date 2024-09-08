"""Utilities to convert HTML and Markdown documents to images."""

from html2text import HTML2Text
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from PIL import Image
import pycmarkgfm as gfm
import regex
from typing import Any, Optional, Type, Union

import src.Directories as Directories
from src.Util.HTML2ImageStrategy import HTML2ImageStrategy, CSSDict, PlaywrightStrategy


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
    html2image_strategy: Type[HTML2ImageStrategy] = PlaywrightStrategy,
) -> Image.Image:
    """Convert HTML to an image using the specified strategy.

    Parameters
    ----------
    html_str : str
        HTML string to convert
    css : Union[str, CSSDict], optional
        CSS string to use for styling, or dict containing selectors as keys and attribute subdicts, by default ""
    width : int, optional
        width of the exported image, by default 1000
    height : int, optional
        height of the exported image; will attempt to get the whole page if None
    crop_transparency : bool, optional
        whether to crop transparency, by default True
    html2image_strategy : HTML2ImageStrategy
        class of the strategy to use for this image conversion, by default PlaywrightStrategy

    Returns
    -------
    Image.Image
        HTML and CSS converted to an image
    """
    return html2image_strategy().to_image(
        html_str=html_str,
        css=css,
        width=width,
        height=height,
        crop_transparency=crop_transparency,
    )


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


def html_to_plaintext(html_str: str) -> str:
    """Convert HTML to plain, unformatted text.

    Parameters
    ----------
    html_str : str
        HTML string to convert

    Returns
    -------
    str
        plain unformatted text with no html elements
    """
    h2t = HTML2Text()
    h2t.ignore_links = True
    h2t.ignore_images = True
    h2t.body_width = 2147483647
    h2t.ul_item_mark = "-"
    h2t.emphasis_mark = ""
    h2t.strong_mark = ""
    # Do some adjustments to make it look better for plaintext
    plaintext = h2t.handle(regex.sub(r"<(/?)h\d>", r"<\1p>", html_str))
    plaintext = regex.sub(r"^\*\s+\*\s+\*$", "-----", plaintext, flags=regex.MULTILINE)
    return plaintext.strip("\n")


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
    plaintext = html_to_plaintext(gfm.gfm_to_html(md_str))
    # Make sure we don't have any escaped characters
    plaintext = regex.sub(r"\\([^\s\\])", r"\1", plaintext).replace("\\\\", "\\")
    return plaintext
