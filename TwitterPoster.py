import io
import json
import os
import twitter

import Directories

class TwitterPoster:
    def __init__(self,
        key_file=os.path.join(Directories.CREDENTIALS_DIR, "twitter.json")
    ):
        key_info = json.load(open(key_file))
        self.__api = twitter.Api(
            consumer_key=key_info["consumer_key"],
            consumer_secret=key_info["consumer_secret"],
            access_token_key=key_info["access_token"],
            access_token_secret=key_info["access_token_secret"]
        )
    
    def make_tweet(self, post_creator):
        # Get the image and text from the post creator
        img = post_creator.get_image()
        if img is not None:
            img_fp = io.BytesIO()
            # Adding attributes to get python-twitter to post image in memory
            img_fp.name = "oc.png"
            img_fp.mode = 'rb'
            img.save(img_fp, format="PNG")
        else:
            img_fp = None
        txt = post_creator.get_text()
        self.__api.PostUpdate(status=txt, media=img_fp)