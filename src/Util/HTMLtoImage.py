"""Utilities to convert HTML and Markdown documents to images."""

import markdown
from pdf2image import convert_from_path
from PIL import Image
import tempfile
from typing import Union
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

CSSDict = dict[str, Union[dict[str, str], list[dict[str, str]]]]
"""Dictionary type containing CSS attributes and values."""


def html_to_image(html: str, css: Union[str, CSSDict] = "", width: int = 1000) -> Image.Image:
    """Convert HTML to an image using `weasyprint` and `pdf2image`.

    Parameters
    ----------
    html : str
        HTML string to convert
    css : Union[str, CSSDict], optional
        CSS string to use for styling, or dict containing selectors as keys and attribute subdicts, by default ""
    width : int, optional
        width of the exported image, by default 1000

    Returns
    -------
    Image.Image
        HTML and CSS converted to an image
    """
    css_str = dict_to_css(css).strip() if isinstance(css, dict) else css
    # Add page size details to CSS
    height = width * 5
    css_str += f"@page {{ size: {width}px {height}px; margin: 0; }}\n"
    html_obj = HTML(string=html, media_type="screen")
    font_config = FontConfiguration()
    css_obj = CSS(string=css_str, font_config=font_config)
    with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
        html_obj.write_pdf(f.name, stylesheets=[css_obj], font_config=font_config)
        images = convert_from_path(f.name, fmt="tiff", transparent=True)
        text_img = images[0]
    # Resize image to match expected width if it doesn't match, for hidpi issues
    text_img_width, text_img_height = text_img.size
    resize_ratio = width / text_img_width
    text_img = text_img.resize((width, int(text_img_height * resize_ratio)))
    return text_img


def md_to_image(md: str, css: Union[str, CSSDict] = "", width: int = 1000) -> Image.Image:
    """Convert Markdown to an image using `html_to_image`.

    Parameters
    ----------
    md : str
        MD string to convert
    css : Union[str, CSSDict], optional
        CSS string to use for styling, or dict containing selectors as keys and attribute subdicts, by default ""
    width : int, optional
        width of the exported image, by default 1000

    Returns
    -------
    Image.Image
        MD and CSS converted to an image
    """
    html = markdown.markdown(md)
    return html_to_image(html, css, width)


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
