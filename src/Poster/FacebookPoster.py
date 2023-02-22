import os
import requests
import tempfile

from .Poster import Poster
from src.PostCreator import PostCreator
from src.Util.HTMLUtil import md_to_plaintext


class FacebookPoster(Poster):
    """Easy poster for Facebook API. Uses access token defined in the following environment variables:

    - `FACEBOOK_ACCESS_TOKEN`
    - `FACEBOOK_PAGE_ID`
    """

    def __init__(self) -> None:
        """Create the Facebook poster using the environment variables described above."""
        self.__access_token = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
        self.__page_id = os.getenv("FACEBOOK_PAGE_ID", "")
        self.__text_url = f"https://graph.facebook.com/{self.__page_id}/feed"
        self.__photo_url = f"https://graph.facebook.com/{self.__page_id}/photos"
        self.__timeout = 15

    def make_post(self, post_creator: PostCreator) -> None:
        """Make a post to Facebook using the given `PostCreator`.

        Parameters
        ----------
        post_creator : PostCreator
            post creator to make the post
        """
        # Set post creator to not prefer long text
        post_creator.prefer_long_text = True
        # Get the image and text from the post creator
        img = post_creator.get_image()
        title_txt = post_creator.get_title()
        if img is None:
            body_txt = post_creator.get_long_text()
            response = requests.post(
                self.__text_url,
                data={
                    "access_token": self.__access_token,
                    "message": md_to_plaintext(f"{title_txt}\n\n{body_txt}"),
                },
                timeout=self.__timeout,
            )
            response.raise_for_status()
        else:
            body_txt = post_creator.get_alt_text() or ""
            with tempfile.NamedTemporaryFile(suffix=".png", mode="w+b") as f:
                # Create a temporary file to post
                img.save(f.name, format="PNG")
                f.seek(0)
                response = requests.post(
                    self.__photo_url,
                    data={
                        "access_token": self.__access_token,
                        "caption": body_txt,
                    },
                    files={
                        "file": f,
                    },
                    timeout=self.__timeout,
                )
                response.raise_for_status()
