from PIL import Image
from typing import Optional, Union

from src.PostCreator.PostCreator import PostCreator


class TweetPostCreator(PostCreator):
    """Creates a post that fits into one tweet.

    Parameters
    ----------
    text : str
        text of the tweet
    tags : Optional[Union[list[str], tuple[str, ...]]], optional
        list of tags for the tweet, by default None
    """

    TWITTER_CHAR_LIMIT = 280
    """Twitter's baked-in character limit"""

    def __init__(self, text: str, tags: Optional[Union[list[str], tuple[str, ...]]] = None, **kwargs):
        self.__text = text
        self.__tags = tags
        super().__init__(**kwargs)

    def get_image(self) -> Optional[Image.Image]:
        """Return no image.

        Returns
        -------
        Optional[Image.Image]
            None since there is no image
        """
        return None

    def get_text(self) -> str:
        """Implements `get_text` in `PostCreator` by using the text and tags of the post. Cuts off content if it exceeds Twitter's character limit.

        Returns
        -------
        str
            text of the post
        """
        content = self.__text
        tags = (" " + " ".join(self.__tags)) if self.__tags is not None else ""
        # Truncate content if it exceeds character limit
        if len(content) + len(tags) > TweetPostCreator.TWITTER_CHAR_LIMIT:
            content = content[: (TweetPostCreator.TWITTER_CHAR_LIMIT - len(tags) - 3)] + "..."
        return content + tags
