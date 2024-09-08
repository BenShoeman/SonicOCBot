from abc import ABC, abstractmethod
import logging
from pathlib import Path
from PIL import Image
import random
from typing import Any, Optional, Union

import src.Directories as Directories


_logger = logging.getLogger(__name__)


def _get_font_choices(fonts_dir: Union[str, Path]) -> dict:
    fonts_path = Path(fonts_dir)
    if fonts_path.exists():
        # Group all fonts with their italic counterparts in the fonts directory
        return {
            font_file.stem.removesuffix("-Regular"): {
                "regular": font_file,
                "italic": font_italic_file
                if (font_italic_file := (fonts_path / f"{font_file.stem.removesuffix('-Regular')}-Italic.ttf")).exists()
                else font_file,
            }
            for font_file in fonts_path.glob("*.ttf")
            if not font_file.stem.endswith("-Italic")
        }
    else:
        _logger.warning(f"could not load fonts as directory {fonts_dir} doesn't exist.")
        return {}


class PostCreator(ABC):
    """Abstract class for post creators."""

    def __init__(self, **kwargs: Any):
        """Post creator default constructor, setting optional kwargs parameters. This should be called in subclass constructors.

        Other Parameters
        ----------------
        **kwargs : dict
            Other keyword arguments to define how the images are created. If omitted, they will get populated as such:
            - prefer_long_text: True
            - regular_font_file: randomly
            - italic_font_file: randomly
        """
        self._prefer_long_text = kwargs.get("prefer_long_text", True)
        # If no font file provided, pick a random one from fonts directory
        self.regular_font_file = kwargs.get("regular_font_file")
        self.italic_font_file = kwargs.get("italic_font_file")
        if self.regular_font_file is None or self.italic_font_file is None:
            font_choices = _get_font_choices(Directories.FONTS_DIR)
            font_name = random.choice(list(font_choices.keys())) if len(font_choices) > 0 else ""
            self.regular_font_file = self.regular_font_file or font_choices.get(font_name, {}).get("regular")
            self.italic_font_file = self.italic_font_file or font_choices.get(font_name, {}).get("italic")

    @property
    def prefer_long_text(self) -> bool:
        """Whether the post should focus on long text, or an image. (e.g., prefer an image for sites with small character limits)

        Returns
        -------
        bool
            whether the post prefers long text
        """
        return self._prefer_long_text

    @prefer_long_text.setter
    def prefer_long_text(self, new: bool) -> None:
        """Set whether the post should focus on long text or an image.

        Parameters
        ----------
        new : bool
            new value for preferring long text
        """
        self._prefer_long_text = new

    @abstractmethod
    def get_image(self) -> Optional[Image.Image]:
        """Returns the image for the post, if there is one.

        Returns
        -------
        Optional[Image.Image]
            image of the post, or None if no image
        """

    @abstractmethod
    def get_alt_text(self, include_title: bool = True) -> Optional[str]:
        """Returns alt text for the post image, if there is alt text.

        Parameters
        ----------
        include_title : bool
            whether to include the post's title in the alt text; by default True

        Returns
        -------
        Optional[str]
            alt text for the post's image, or None if there is none
        """

    @abstractmethod
    def get_title(self) -> Optional[str]:
        """Returns the title for the post, if applicable.

        Returns
        -------
        Optional[str]
            title of the post, or None if there is none
        """

    @abstractmethod
    def get_short_text(self) -> str:
        """Returns the short text for the post.

        Returns
        -------
        str
            short text of the post
        """

    @abstractmethod
    def get_long_text(self) -> str:
        """Returns the long text for the post.

        Returns
        -------
        str
            long text of the post
        """

    @abstractmethod
    def get_tags(self) -> Optional[tuple[str, ...]]:
        """Returns all tags for the post image, if there are any.

        Returns
        -------
        Optional[tuple[str, ...]]
            tuple of tags for the post, or None if there are none
        """
