from PIL import Image
from typing import Any, Optional

from .PostCreator import PostCreator


class TwitterPostCreator(PostCreator):
    """`PostCreator` that makes a child `PostCreator` obey Twitter character limits."""

    def __init__(self, post_creator: PostCreator, post_char_limit: int = 280, alt_char_limit: int = 1000, **kwargs: Any):
        """Creates a `TwitterPostCreator`.

        Parameters
        ----------
        post_creator : PostCreator
            the post creator to impose character limits on
        post_char_limit : int, optional
            tweet character limit, by default 280
        alt_char_limit : int, optional
            alt text character limit, by default 1000
        """
        self.__post_creator = post_creator
        self.__post_char_limit = post_char_limit
        self.__alt_char_limit = alt_char_limit

    @property
    def prefer_long_text(self) -> bool:
        """Gets `prefer_long_text` from the child poster.

        Returns
        -------
        bool
            whether the post prefers long text
        """
        return self.__post_creator.prefer_long_text

    @prefer_long_text.setter
    def prefer_long_text(self, new: bool) -> None:
        """Passes on `prefer_long_text` value to the child poster.

        Parameters
        ----------
        new : bool
            new value for preferring long text
        """
        self.__post_creator.prefer_long_text = new

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

    def get_title(self) -> Optional[str]:
        """Returns the result of the child's `get_title` post (though it will be unused for tweets).

        Returns
        -------
        Optional[str]
            title of the post
        """
        return self.__post_creator.get_title()

    def get_short_text(self) -> str:
        """Returns the short text for the post, truncated to Twitter's tweet character limit.

        Returns
        -------
        str
            short text of the post
        """
        post_text = self.__post_creator.get_short_text()
        if len(post_text) <= self.__post_char_limit:
            return post_text
        else:
            return post_text[: self.__post_char_limit - 3] + "..."

    def get_long_text(self) -> str:
        """Returns the result of the child's `get_long_text` post (though it will be unused for tweets).

        Returns
        -------
        str
            long text of the post
        """
        return self.__post_creator.get_long_text()

    def get_tags(self) -> Optional[tuple[str, ...]]:
        """Returns the result of the child's `get_tags` post (though it will be unused for tweets).

        Returns
        -------
        Optional[tuple[str, ...]]
            tags of the post
        """
        return self.__post_creator.get_tags()
