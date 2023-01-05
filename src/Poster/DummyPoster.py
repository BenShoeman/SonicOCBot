import logging

from .Poster import Poster
from src.PostCreator import PostCreator


_logger = logging.getLogger(__name__)


class DummyPoster(Poster):
    """Fake poster that just logs the description and shows the image."""

    def __init__(self, prefer_long_text: bool = True, show_image: bool = True):
        """Create `DummyPoster` with an option to make the post creator prefer long text.

        Parameters
        ----------
        prefer_long_text : bool, optional
            whether to force the post creator to prefer long text, by default True
        show_image : bool, optional
            whether to show the image using Pillow's Image.show method, by default True
        """
        self.__force_prefer_long_text = prefer_long_text
        self.__show_image = show_image

    def make_post(self, post_creator: PostCreator) -> None:
        """Fake a post using the given `PostCreator` by logging the description and showing the image.

        Parameters
        ----------
        post_creator : PostCreator
            post creator to make the post
        """
        post_creator.prefer_long_text = self.__force_prefer_long_text
        # Log different stuff depending on whether long text is preferred
        if self.__force_prefer_long_text:
            _logger.info(f"Title: {post_creator.get_title()}")
            _logger.info(f"Long Text: {post_creator.get_long_text()}")
        else:
            _logger.info(f"Short Text: {post_creator.get_short_text()}")
            _logger.info(f"Alt Text: {post_creator.get_alt_text()}")
        _logger.info(f"Tags: {post_creator.get_tags()}")
        img = post_creator.get_image()
        if self.__show_image and img is not None:
            img.show()
