from datetime import datetime
import json
import os
from PIL import Image
import tempfile
import tweepy

import src.Directories as Directories
from src.PostCreator.PostCreator import PostCreator


class TwitterPoster:
    """Easy interface for Twitter API. Uses consumer and access token key/secret defined in the following environment variables:

    - `twitter_consumer_key`
    - `twitter_consumer_secret`
    - `twitter_access_token`
    - `twitter_access_token_secret`
    """

    def __init__(self):
        auth = tweepy.OAuth1UserHandler(
            consumer_key=os.environ["twitter_consumer_key"],
            consumer_secret=os.environ["twitter_consumer_secret"],
            access_token=os.environ["twitter_access_token"],
            access_token_secret=os.environ["twitter_access_token_secret"],
        )
        self.__api: tweepy.API = tweepy.API(auth, wait_on_rate_limit=True)

    def make_tweet(self, post_creator: PostCreator) -> None:
        # Get the image and text from the post creator
        img = post_creator.get_image()
        img_filepath = os.path.join(tempfile.gettempdir(), f"sonicocbot-{datetime.now().strftime('%Y%m%d-%H%M%S')}.png") if img is not None else None
        if img is not None and img_filepath is not None:
            # Create a temporary file to post
            img.save(img_filepath, format="PNG")
        else:
            img = None
        post_txt = post_creator.get_text()
        alt_txt = post_creator.get_alt_text()
        media = self.__api.media_upload(img_filepath)
        if alt_txt is not None:
            self.__api.create_media_metadata(media.media_id, alt_txt)
        self.__api.update_status(status=post_txt, media_ids=[media.media_id])
        if img_filepath is not None:
            os.remove(img_filepath)
