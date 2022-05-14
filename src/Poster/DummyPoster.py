from .Poster import Poster
from src.PostCreator import PostCreator


class DummyPoster(Poster):
    """Fake poster that just prints the description and shows the image."""

    def make_post(self, post_creator: PostCreator):
        """Fake a post using the given `PostCreator` by printing the description and showing the image.

        Parameters
        ----------
        post_creator : PostCreator
            post creator to make the post
        """
        print(post_creator.get_text())
        img = post_creator.get_image()
        if img is not None:
            img.show()
