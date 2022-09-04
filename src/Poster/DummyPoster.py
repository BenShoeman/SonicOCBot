from .Poster import Poster
from src.PostCreator import PostCreator


class DummyPoster(Poster):
    """Fake poster that just prints the description and shows the image."""

    def __init__(self, prefer_long_text: bool = True):
        """Create `DummyPoster` with an option to make the post creator prefer long text.

        Parameters
        ----------
        prefer_long_text : bool, optional
            whether to force the post creator to prefer long text, by default True
        """
        self.__force_prefer_long_text = prefer_long_text

    def make_post(self, post_creator: PostCreator) -> None:
        """Fake a post using the given `PostCreator` by printing the description and showing the image.

        Parameters
        ----------
        post_creator : PostCreator
            post creator to make the post
        """
        post_creator.prefer_long_text = self.__force_prefer_long_text
        # Print different stuff depending on whether long text is preferred
        if self.__force_prefer_long_text:
            print("Title:", post_creator.get_title())
            print("Long Text:", post_creator.get_long_text())
        else:
            print("Short Text:", post_creator.get_short_text())
            print("Alt Text:", post_creator.get_alt_text())
        print("Tags:", post_creator.get_tags())
        img = post_creator.get_image()
        if img is not None:
            img.show()
