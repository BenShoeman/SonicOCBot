from PIL import Image
from typing import Any, Optional, Union

from .HTMLPostCreator import HTMLPostCreator
from src.Util.HTMLUtil import md_to_plaintext
from src.OC import OC


class OCHTMLPostCreator(HTMLPostCreator):
    """`HTMLPostCreator` that creates a post involving an OC."""

    def __init__(self, oc: OC, tags: Optional[Union[list[str], tuple[str, ...]]] = ("oc bot",), **kwargs: Any):
        """Create an `OCHTMLPostCreator`.

        Parameters
        ----------
        oc : OC
            `OC` object to create a post for
        tags : Optional[Union[list[str], tuple[str, ...]]], optional
            list of tags to be used in the post, by default ("oc bot",)

        Other Parameters
        ----------------
        **kwargs : dict
            Same as in `HTMLPostCreator`.
        """
        self.__oc = oc
        # Pre-crop OC image for laying out better
        bbox = oc.image.getbbox()
        oc_img = oc.image.crop(bbox)
        super().__init__(
            content=self.__get_oc_text(include_name=False),
            title=f"{oc.name} the {oc.species.title()}",
            subtitle=oc.pronouns,
            image=oc_img,
            use_markdown=True,
            tags=tags,
            **kwargs,
        )

    def get_image(self) -> Optional[Image.Image]:
        """Implements `get_image` in `PostCreator` by creating an image, using the image and description from the `OC`.

        Returns
        -------
        Optional[Image.Image]
            image of the post
        """
        # Since prefer_long_text can change after creation, reset these as required based on height
        self._post_width = round(self._post_height * (4 / 3 if self._prefer_long_text else 30 / 17))
        return super().get_image()

    def get_alt_text(self) -> Optional[str]:
        """Implements `get_alt_text` in `PostCreator` by using the description of the `OC`.

        Returns
        -------
        Optional[str]
            alt text of the post from the `OC` description
        """
        return self.__get_oc_text(use_markdown=False)

    def get_title(self) -> Optional[str]:
        """Implements `get_title` in `PostCreator` by using the name and species of the `OC`.

        Returns
        -------
        Optional[str]
            title of the post
        """
        oc = self.__oc
        return f"{oc.name} the {oc.species.title()}"

    def get_short_text(self) -> str:
        """Implements `get_short_text` in `PostCreator` by using the name and species of the `OC`.

        Returns
        -------
        str
            short text of the post
        """
        oc = self.__oc
        return f"{oc.name} the {oc.species.title()} {' '.join('#' + tag.replace(' ', '') for tag in self._tags) if self._tags else ''}"

    def get_long_text(self) -> str:
        """Implements `get_long_text` in `PostCreator` by using the description of the `OC`.

        Returns
        -------
        str
            long text of the post
        """
        return self.__get_oc_text()

    def __get_oc_text(self, use_markdown: bool = True, include_name: bool = True) -> str:
        """Compile information about the `OC` into one string for use in the post image.

        Returns
        -------
        str
            full text blurb of the `OC` to put in the post image
        """

        def md(tag: str, fallback: str = "") -> str:
            return tag if use_markdown else fallback

        oc = self.__oc
        oc_text = ""
        if include_name:
            oc_text += f"{md('# ')}{oc.name} the {oc.species.title()} "
            oc_text += f"{md('<span class=small>*','(')}{oc.pronouns}{md('*</span>',')')}\n\n"
        oc_text += f"{md('- ')}Age: {oc.age}\n"
        oc_text += f"{md('- ')}Height: {oc.height}\n"
        oc_text += f"{md('- ')}Weight: {oc.weight}\n"
        oc_text += f"{md('- ')}Traits: {', '.join(oc.personalities).title()}\n"
        oc_text += f"{md('- ')}Skills: {', '.join(oc.skills).title()}\n"
        for k, v in sorted(oc.fill_regions.items(), key=lambda kv: kv[0]):
            oc_text += f"{md('- ')}{k.title()}: {v.title()}\n"
        if use_markdown:
            oc_text += "\n-----\n"
        oc_text += f"\n{md_to_plaintext(oc.description)}"
        return oc_text
