from PIL import Image
from typing import Optional

from .PostCreator import PostCreator


class TwitterPostCreator(PostCreator):
    """`PostCreator` that makes a child `PostCreator` obey Twitter character limits."""

    def __init__(self, post_creator: PostCreator, post_char_limit: int = 280, alt_char_limit: int = 1000, **kwargs):
        self.__post_creator = post_creator
        self.__post_char_limit = post_char_limit
        self.__alt_char_limit = alt_char_limit

    def get_image(self) -> Optional[Image.Image]:
        """Returns the image for the child post creator.

        Returns
        -------
        Optional[Image.Image]
            image of the post, or None if no image
        """
        return self.__post_creator.get_image()

    def get_alt_text(self) -> Optional[str]:
        """Returns alt text for the post image, truncated to Twitter's alt text character limit.

        Returns
        -------
        Optional[str]
            alt text for the post's image, or None if there is none
        """
        alt_text = self.__post_creator.get_alt_text()
        if alt_text is None or len(alt_text) <= self.__alt_char_limit:
            return alt_text
        else:
            return alt_text[: self.__alt_char_limit - 3] + "..."

    def get_text(self) -> str:
        """Returns the text for the post, truncated to Twitter's tweet character limit.

        Returns
        -------
        str
            text of the post
        """
        post_text = self.__post_creator.get_text()
        if len(post_text) <= self.__post_char_limit:
            return post_text
        else:
            return post_text[: self.__post_char_limit - 3] + "..."
