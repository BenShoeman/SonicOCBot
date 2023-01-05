from mastodon import Mastodon
import os
import tempfile

from .Poster import Poster
from src.PostCreator import PostCreator


class MastodonPoster(Poster):
    """Easy poster for Mastodon API. Uses instance and access token defined in the following environment variables:

    - `MASTODON_INSTANCE_URL`
    - `MASTODON_ACCESS_TOKEN`
    """

    def __init__(self) -> None:
        """Create the Mastodon poster using the environment variables described above."""
        self.__api = Mastodon(
            access_token=os.environ.get("MASTODON_ACCESS_TOKEN"),
            api_base_url=os.environ.get("MASTODON_INSTANCE_URL", "https://localhost"),
        )

    def make_post(self, post_creator: PostCreator) -> None:
        """Make a post to Mastodon using the given `PostCreator`.

        Parameters
        ----------
        post_creator : PostCreator
            post creator to make the post
        """
        # Set post creator to not prefer long text
        post_creator.prefer_long_text = False
        # Get the image and text from the post creator
        img = post_creator.get_image()
        post_txt = post_creator.get_short_text()
        alt_txt = post_creator.get_alt_text()
        if img is None:
            self.__api.status_post(status=post_txt)
        else:
            with tempfile.NamedTemporaryFile(suffix=".png") as f:
                # Create a temporary file to post
                img.save(f.name, format="PNG")
                media = self.__api.media_post(media_file=f.name, description=alt_txt)
                self.__api.status_post(status=post_txt, media_ids=media)
