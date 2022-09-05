from datetime import datetime
from PIL import Image
from typing import Any, Optional, Union

from .PostCreator import PostCreator
from src.OC import OC
from src.Util.ColorUtil import to_pil_color_tuple
from src.Util.HTMLtoImage import md_to_image


class OCPostCreator(PostCreator):
    """`PostCreator` that creates a post involving an OC."""

    def __init__(self, oc: OC, tags: Optional[Union[list[str], tuple[str, ...]]] = ("ocbot",), **kwargs: Any):
        """Create a `OCPostCreator`.

        Parameters
        ----------
        oc : OC
            `OC` object to create a post for
        tags : Optional[Union[list[str], tuple[str, ...]]], optional
            list of tags to be used in the post, by default ("ocbot",)

        Other Parameters
        ----------------
        **kwargs : dict
            Same as in `PostCreator`.
        """
        self.__oc = oc
        self.__tags = tags
        super().__init__(**kwargs)

    def get_image(self) -> Optional[Image.Image]:
        """Implements `get_image` in `PostCreator` by creating an image, using the image and description from the `OC`.

        Returns a much more minimal image with just the OC's name if `prefer_long_text` is True.

        Returns
        -------
        Optional[Image.Image]
            image of the post
        """
        # Get colors/images that will be used regardless of if long text is preferred or not
        post_img_margin = 20
        current_time = datetime.now().time()
        bgcolor = self._get_bgcolor_for_time(current_time)
        textcolor = self._get_textcolor_for_time(current_time)
        oc_img = self.__oc.image
        self.generate_css(textcolor)

        if self.prefer_long_text:
            post_img_width, post_img_height = (680, 680)
            post_img = Image.new("RGB", (post_img_width, post_img_height), to_pil_color_tuple(bgcolor))
            text_img = md_to_image(f"# {self.__oc.name} the {self.__oc.species.title()}", css=self._md_css, width=post_img_width - 2 * post_img_margin)
            # Crop transparency in image
            bbox = text_img.getbbox()
            text_img = text_img.crop(bbox)

            # Put text image at the bottom
            text_img_width, text_img_height = text_img.size
            post_img.paste(text_img, (post_img_width // 2 - text_img_width // 2, post_img_height - post_img_margin - text_img_height), text_img)

            # Make OC image fill the rest of the available space above the text
            bbox = oc_img.getbbox()
            oc_img = oc_img.crop(bbox)
            oc_width, oc_height = oc_img.size
            post_oc_ratio = (post_img_height - 3 * post_img_margin - text_img_height) / oc_height
            oc_img_resized = oc_img.resize((int(oc_width * post_oc_ratio), int(oc_height * post_oc_ratio)))
            new_oc_width, new_oc_height = oc_img_resized.size
            post_img.paste(oc_img_resized, (post_img_width // 2 - new_oc_width // 2, post_img_margin), oc_img_resized)
        else:
            # Initialize the new image
            post_img_width, post_img_height = (1200, 680)
            post_img = Image.new("RGB", (post_img_width, post_img_height), to_pil_color_tuple(bgcolor))

            # Position the OC on left side of the image
            oc_width, oc_height = oc_img.size
            post_oc_ratio = (post_img_height - 2 * post_img_margin) / oc_height
            oc_img_resized = oc_img.resize((int(oc_width * post_oc_ratio), int(oc_height * post_oc_ratio)))
            new_oc_width, new_oc_height = oc_img_resized.size
            post_img.paste(oc_img_resized, (0, post_img_margin), oc_img_resized)

            text_img = md_to_image(self.__get_oc_text(), css=self._md_css, width=post_img_width - new_oc_width - 3 * post_img_margin)
            # Crop transparency in image
            bbox = text_img.getbbox()
            text_img = text_img.crop(bbox)

            # Squish text_img to fit height if it exceeds height and place on right side of the image
            text_img_width, text_img_height = text_img.size
            if text_img_height > post_img_height - 2 * post_img_margin:
                text_img_height = post_img_height - 2 * post_img_margin
                text_img = text_img.resize((text_img_width, text_img_height))
            post_img.paste(text_img, (new_oc_width + 2 * post_img_margin, post_img_height // 2 - text_img_height // 2), text_img)

        return post_img

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
        return f"{oc.name} the {oc.species.title()} {' '.join('#' + tag.replace(' ', '') for tag in self.__tags) if self.__tags else ''}"

    def get_long_text(self) -> str:
        """Implements `get_long_text` in `PostCreator` by using the description of the `OC`.

        Returns
        -------
        str
            long text of the post
        """
        return self.__get_oc_text()

    def __get_oc_text(self, use_markdown: bool = True) -> str:
        """Compile information about the `OC` into one string for use in the post image.

        Returns
        -------
        str
            full text blurb of the `OC` to put in the post image
        """

        def md(tag: str, fallback: str = "") -> str:
            return tag if use_markdown else fallback

        oc = self.__oc
        oc_text = f"{md('# ')}{oc.name} the {oc.species.title()} "
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
        oc_text += f"\n{oc.description}"
        return oc_text

    def get_tags(self) -> Optional[tuple[str, ...]]:
        return tuple(self.__tags) if self.__tags else None
