from datetime import datetime
from html2image import Html2Image
import markdown
import os
from PIL import Image
import tempfile
from typing import Union

CSSDict = dict[str, Union[dict[str, str], list[dict[str, str]]]]


def html_to_image(html: str, css: Union[str, CSSDict] = "", width: int = 1000) -> Image.Image:
    """Convert HTML to an image.

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
    html2img = Html2Image(output_path=tempfile.gettempdir(), size=(width, width * 5))
    tempfile_name = f"html2img-{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"
    text_img_path = os.path.join(tempfile.gettempdir(), tempfile_name)
    html2img.screenshot(html_str=html, css_str=css_str if len(css) > 0 else [], save_as=tempfile_name)
    text_img = Image.open(text_img_path)
    os.remove(text_img_path)
    return text_img


def md_to_image(md: str, css: Union[str, CSSDict] = "", width: int = 1000) -> Image.Image:
    """Convert Markdown to an image.

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
