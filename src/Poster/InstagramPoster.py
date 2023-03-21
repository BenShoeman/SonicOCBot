import os
import requests

from .Poster import Poster
from src.PostCreator import PostCreator, OCHTMLPostCreator
from src.Util.ImageUtil import imgur_upload, imgur_delete


class InstagramPoster(Poster):
    """Easy poster for Instagram API. Uses access token defined in the following environment variables:

    - `FACEBOOK_ACCESS_TOKEN`
    - `INSTAGRAM_USER_ID`

    Very similar to FacebookPoster, but uses Instagram endpoints instead of Facebook.
    """

    def __init__(self) -> None:
        """Create the Instagram poster using the environment variables described above."""
        self.__access_token = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
        self.__instagram_user_id = os.getenv("INSTAGRAM_USER_ID", "")
        self.__base_url = f"https://graph.facebook.com/{self.__instagram_user_id}"
        self.__timeout = 15

    def make_post(self, post_creator: PostCreator) -> None:
        """Make a post to Instagram using the given `PostCreator`.

        Parameters
        ----------
        post_creator : PostCreator
            post creator to make the post
        """
        # Set post creator to prefer long text for OC posts since those have better formatted photos, but not for other post types
        post_creator.prefer_long_text = isinstance(post_creator, OCHTMLPostCreator)
        # Get the image and text from the post creator
        img = post_creator.get_image()
        title_txt = post_creator.get_title()
        if img is None:
            raise NotImplementedError("Posting text only to Instagram is not supported")
        else:
            # Instagram API requires existing image URL, so do temporary upload first
            img_upload = imgur_upload(img)
            try:
                # Use the short text and alt text for body text
                body_txt = f"{post_creator.get_short_text()}\n\n{post_creator.get_alt_text(include_title=False)}"
                upload_response = requests.post(
                    f"{self.__base_url}/media",
                    params={
                        "access_token": self.__access_token,
                        "image_url": img_upload["url"],
                        "caption": body_txt,
                    },
                    timeout=self.__timeout,
                )
                upload_response.raise_for_status()
                publish_response = requests.post(
                    f"{self.__base_url}/media_publish",
                    params={
                        "access_token": self.__access_token,
                        "creation_id": upload_response.json()["id"],
                    },
                    timeout=self.__timeout,
                )
                publish_response.raise_for_status()
            # Delete the image from Imgur regardless of success or not
            except Exception as e:
                imgur_delete(img_upload["delete_hash"])
                raise e
            else:
                imgur_delete(img_upload["delete_hash"])
