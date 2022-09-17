from datetime import datetime
from PIL import Image, ImageDraw
from typing import Any, Optional, Union

from .PostCreator import PostCreator
from src.Util.HTMLtoImage import md_to_image
from src.Util.ColorUtil import ColorTuple, to_pil_color_tuple


class TextPostCreator(PostCreator):
    """`PostCreator` that creates a post having an image with text on it."""

    def __init__(self, text: str, title: Optional[str] = None, tags: Optional[Union[list[str], tuple[str, ...]]] = None, **kwargs: Any):
        """Create a `TextPostCreator`.

        Parameters
        ----------
        text : str
            text to make image of
        title : Optional[str], optional
            title of the text in the image, by default None
        tags : Optional[Union[list[str], tuple[str, ...]]], optional
            list of tags to be used in the text of the post, by default None

        Other Parameters
        ----------------
        **kwargs : dict
            Same as in `PostCreator`.
        """
        self.__text = text
        self.__title = title
        self.__tags = tags
        self.__banner_img: Optional[Image.Image] = None
        self.__banner_bgcolor: Optional[tuple[int, int, int]] = None
        self.__banner_height = 0
        self.__overlay_img: Optional[Image.Image] = None
        self.__overlay_alpha = 0
        super().__init__(**kwargs)

    def set_banner(self, img: Optional[Union[str, Image.Image]] = None, bgcolor: Optional[ColorTuple] = None, height: int = 80) -> None:
        """Set the top banner logo (e.g., to imitate a specific site).

        Parameters
        ----------
        img : Optional[Image.Image], optional
            logo to put in the upper left corner of the banner, or None to remove banner
        bgcolor : Optional[ColorTuple], optional
            color to make the banner; if None, uses the average color of the image corners; by default None
        height : int, optional
            height of the banner, by default 100
        """
        if isinstance(img, str):
            self.__banner_img = Image.open(img)
        else:
            self.__banner_img = img
        if self.__banner_img is not None:
            if bgcolor is not None:
                r, g, b = bgcolor
                self.__banner_bgcolor = (int(r), int(g), int(b))
            else:
                # Set background color based on the corners of the image
                img_rgb = self.__banner_img.convert("RGB")
                img_width, img_height = img_rgb.size
                corners = (
                    img_rgb.getpixel((0, 0)),
                    img_rgb.getpixel((img_width - 1, img_height - 1)),
                    img_rgb.getpixel((img_width - 1, 0)),
                    img_rgb.getpixel((0, img_height - 1)),
                )
                # Color will be average of 4 corner colors
                self.__banner_bgcolor = (
                    (corners[0][0] + corners[1][0] + corners[2][0] + corners[3][0]) // 4,
                    (corners[0][1] + corners[1][1] + corners[2][1] + corners[3][1]) // 4,
                    (corners[0][2] + corners[1][2] + corners[2][2] + corners[3][2]) // 4,
                )
            self.__banner_height = height
        else:
            self.__banner_bgcolor = None
            self.__banner_height = 0

    def set_overlay(self, img: Optional[Union[str, Image.Image]] = None, alpha: int = 255) -> None:
        """Set the background overlay image.

        Parameters
        ----------
        img : Optional[Image.Image], optional
            image to overlay in the background, or None to remove it
        alpha : int, optional
            alpha to paste the image at in interval [0, 255], by default 255
        """
        if isinstance(img, str):
            self.__overlay_img = Image.open(img)
        else:
            self.__overlay_img = img
        if self.__overlay_img is not None:
            self.__overlay_alpha = alpha
        else:
            self.__overlay_alpha = 0

    def get_image(self) -> Optional[Image.Image]:
        """Implements `get_image` in `PostCreator` by creating an image, using the title and text of the post.

        If `prefer_long_text` is True, then no image is returned.

        Returns
        -------
        Optional[Image.Image]
            image of the post, or None if long text is preferred
        """
        if self.prefer_long_text:
            return None
        else:
            current_time = datetime.now().time()
            img_width, img_height = (1200, 680)
            img_hmargin, img_vmargin = (50, 20)
            banner_height = self.__banner_height if self.__banner_img is not None else 0
            bgcolor = self._get_bgcolor_for_time(current_time)
            textcolor = self._get_textcolor_for_time(current_time)
            post_img = Image.new("RGB", (img_width, img_height), to_pil_color_tuple(bgcolor))

            # Draw the overlay image if there is one
            if self.__overlay_img is not None:
                orig_overlay_width, orig_overlay_height = self.__overlay_img.size
                resize_ratio = (img_height - banner_height) / orig_overlay_height
                overlay_img: Image.Image = self.__overlay_img.convert("RGBA").resize((int(orig_overlay_width * resize_ratio), img_height - banner_height))
                overlay_width, overlay_height = overlay_img.size
                # Apply alpha to image by modifying alpha channel
                alpha_chnl: Image.Image = overlay_img.getchannel("A").convert("RGBA")
                alpha_dim = Image.new("RGBA", (overlay_width, overlay_height), (0, 0, 0, 255 - self.__overlay_alpha))
                alpha_chnl.alpha_composite(alpha_dim)
                post_img.paste(overlay_img, (0, banner_height), alpha_chnl.convert("L"))

            # Draw the banner at the top if there is a logo
            if self.__banner_img is not None and self.__banner_bgcolor is not None:
                img_draw = ImageDraw.Draw(post_img)
                img_draw.rectangle((0, 0, img_width, banner_height), fill=self.__banner_bgcolor)
                del img_draw
                logo_width, logo_height = self.__banner_img.size
                new_logo_height = banner_height - 2 * img_vmargin
                resize_ratio = new_logo_height / logo_height
                new_logo_width = int(logo_width * resize_ratio)
                logo_resized = self.__banner_img.convert("RGBA").resize((new_logo_width, new_logo_height))
                post_img.paste(logo_resized, (img_width // 2 - new_logo_width // 2, img_vmargin), logo_resized)

            post_text = (f"# {self.__title}\n\n" if self.__title is not None else "") + self.__text.replace("\n", "\n\n")

            self.generate_css(textcolor)
            text_img = md_to_image(post_text, css=self._md_css, width=img_width - 2 * img_hmargin)

            # Squish text_img to fit height if it exceeds height
            text_img_width, text_img_height = text_img.size
            if text_img_height > img_height - 2 * img_vmargin - banner_height:
                text_img_height = img_height - 2 * img_vmargin - banner_height
                text_img = text_img.resize((text_img_width, text_img_height))
            post_img.paste(text_img, (img_hmargin, img_height // 2 - text_img_height // 2 + banner_height // 2), text_img)
            return post_img

    def get_alt_text(self) -> str:
        """Implements `get_alt_text` in `PostCreator` by using the text in the post image.

        Returns
        -------
        str
            alt text using the text in the image
        """
        single_newline = "\n"
        double_newline = "\n\n"
        return f"{(self.__title + double_newline) if self.__title else ''}{self.__text.replace(single_newline, double_newline)}"

    def get_title(self) -> Optional[str]:
        """Implements `get_title` in `PostCreator` by returning the title of the post.

        Returns
        -------
        Optional[str]
            title of the post
        """
        return self.__title

    def get_short_text(self) -> str:
        """Implements `get_short_text` in `PostCreator` by using the title or text, and tags of the post.

        Returns
        -------
        str
            short text of the post
        """
        tags_suffix = " " + " ".join(f"#{tag.replace(' ', '')}" for tag in self.__tags) if self.__tags else ""
        # Use title if there is one, otherwise the text
        content = self.__title or self.__text
        content += tags_suffix
        return content

    def get_long_text(self) -> str:
        """Implements `get_long_text` in `PostCreator` by returning the text of the post.

        Returns
        -------
        str
            long text of the post
        """
        return self.__text.replace("\n", "\n\n")

    def get_tags(self) -> Optional[tuple[str, ...]]:
        """Implements `get_tags` in `PostCreator` by returning the tuple of tags.

        Returns
        -------
        Optional[tuple[str, ...]]
            tags of the post
        """
        return tuple(self.__tags) if self.__tags else None
