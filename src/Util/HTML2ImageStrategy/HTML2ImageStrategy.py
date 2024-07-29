"""
Different strategies for converting HTML to image. Since the state of such tools is constantly
in flux, the need to change this easily is necessary.
"""

from abc import ABC, abstractmethod
from PIL import Image
from typing import Optional, Union

CSSDict = dict[str, Union[dict[str, str], list[dict[str, str]]]]
"""Dictionary type containing CSS attributes and values."""


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


class HTML2ImageStrategy(ABC):
    """Represents a strategy to convert HTML/CSS to an image."""

    def __init__(self) -> None:
        """Create a `HTML2ImageStrategy`."""

    @abstractmethod
    def to_image(
        self,
        html_str: str,
        css: Union[str, CSSDict] = "",
        width: int = 1000,
        height: Optional[int] = None,
        crop_transparency: bool = True,
    ) -> Image.Image:
        """Convert HTML to an image.

        Parameters
        ----------
        html_str : str
            HTML string to convert
        css : Union[str, CSSDict], optional
            CSS string to use for styling, or dict containing selectors as keys and attribute subdicts, by default ""
        width : int, optional
            width of the exported image, by default 1000
        height : int, optional
            height of the exported image; if not provided, should get the whole page if possible
        crop_transparency : bool, optional
            whether to crop transparency, by default True

        Returns
        -------
        Image.Image
            HTML and CSS converted to an image
        """
