from pathlib import Path
import random
from typing import Any, ClassVar, List, Optional, Union

from .HTMLPostCreator import HTMLPostCreator
import src.Directories as Directories
from src.SonicSezGenerator import SonicSezGenerator


class SonicSezHTMLPostCreator(HTMLPostCreator):
    """`HTMLPostCreator` that creates a post with a Sonic Says segment generator."""

    _bg_images: ClassVar[List[Path]] = list((Directories.IMAGES_DIR / "sonicsez").glob("*.png"))

    def __init__(self, sonicsez_generator: SonicSezGenerator, tags: Optional[Union[list[str], tuple[str, ...]]] = ("sonic says", "sonic sez"), **kwargs: Any):
        """Create a `SonicSezHTMLPostCreator`.

        Parameters
        ----------
        sonicsez_generator : SonicSezGenerator
            `SonicSezGenerator` object to create a post using
        tags : Optional[Union[list[str], tuple[str, ...]]], optional
            list of tags to be used in the post, by default ("sonic says", "sonic sez")

        Other Parameters
        ----------------
        **kwargs : dict
            Same as in `HTMLPostCreator`.
        """
        self.__ssez_generator = sonicsez_generator
        text = sonicsez_generator.get_text()
        overlay_path = random.choice(self.__class__._bg_images) if len(self.__class__._bg_images) > 0 else None
        super().__init__(
            content=text,
            title="Sonic Says...",
            overlay_path=overlay_path,
            use_markdown=True,
            tags=tags,
            **kwargs,
        )
