from pathlib import Path
import random
from typing import Any, ClassVar, List, Optional, Union

from .HTMLPostCreator import HTMLPostCreator
import src.Directories as Directories
from src.FanfictionGenerator import FanfictionGenerator


class FanficHTMLPostCreator(HTMLPostCreator):
    """`HTMLPostCreator` that creates a post with a fanfic generator."""

    _logo_images: ClassVar[List[Path]] = list((Directories.IMAGES_DIR / "fanficlogo").glob("*.png"))

    def __init__(self, fanfic_generator: FanfictionGenerator, tags: Optional[Union[list[str], tuple[str, ...]]] = ("fanfic bot",), **kwargs: Any):
        """Create a `FanficHTMLPostCreator`.

        Parameters
        ----------
        fanfic_generator : FanfictionGenerator
            `FanfictionGenerator` object to create a post using
        tags : Optional[Union[list[str], tuple[str, ...]]], optional
            list of tags to be used in the post, by default ("fanfic bot",)

        Other Parameters
        ----------------
        **kwargs : dict
            Same as in `HTMLPostCreator`.
        """
        self.__ffic_generator = fanfic_generator
        fanfic_title, fanfic_text = fanfic_generator.get_fanfiction()
        header_path = random.choice(self.__class__._logo_images) if len(self.__class__._logo_images) > 0 else None
        super().__init__(
            content=fanfic_text,
            title=fanfic_title,
            header_path=header_path,
            use_markdown=True,
            tags=tags,
            **kwargs,
        )
