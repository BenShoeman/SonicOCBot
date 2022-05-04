from src.PostCreator.PostCreator import PostCreator
from src.Poster.Poster import Poster


class DummyPoster(Poster):
    """Fake poster that just prints the description and shows the image."""

    def make_post(self, post_creator: PostCreator):
        print(post_creator.get_text())
        img = post_creator.get_image()
        if img is not None:
            img.show()
