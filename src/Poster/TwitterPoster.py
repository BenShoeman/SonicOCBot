import os
import tempfile
import tweepy

from .Poster import Poster
from src.PostCreator import PostCreator


class TwitterPoster(Poster):
    """Easy poster for Twitter API. Uses consumer and access token key/secret defined in the following environment variables:

    - `TWITTER_CONSUMER_KEY`
    - `TWITTER_CONSUMER_SECRET`
    - `TWITTER_ACCESS_TOKEN`
    - `TWITTER_ACCESS_TOKEN_SECRET`
    """

    def __init__(self) -> None:
        """Create the Twitter poster using the environment variables described above."""
        auth = tweepy.OAuth1UserHandler(
            consumer_key=os.environ.get("TWITTER_CONSUMER_KEY", ""),
            consumer_secret=os.environ.get("TWITTER_CONSUMER_SECRET", ""),
            access_token=os.environ.get("TWITTER_ACCESS_TOKEN"),
            access_token_secret=os.environ.get("TWITTER_ACCESS_TOKEN_SECRET"),
        )
        self.__api: tweepy.API = tweepy.API(auth, wait_on_rate_limit=True)

    def make_post(self, post_creator: PostCreator) -> None:
        """Make a post to Twitter using the given `PostCreator`.

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
            self.__api.update_status(status=post_txt)
        else:
            with tempfile.NamedTemporaryFile(suffix=".png") as f:
                # Create a temporary file to post
                img.save(f.name, format="PNG")
                media = self.__api.media_upload(f.name)
                if alt_txt is not None:
                    self.__api.create_media_metadata(media.media_id, alt_txt)
                self.__api.update_status(status=post_txt, media_ids=[media.media_id])
