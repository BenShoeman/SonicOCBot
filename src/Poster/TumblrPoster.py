import os
import pytumblr
import tempfile

from .Poster import Poster
from src.PostCreator import PostCreator, OCPostCreator, TextPostCreator


class TumblrPoster(Poster):
    """Easy poster for Tumblr API. Uses consumer and OAuth token/secret defined in the following environment variables:

    - `TUMBLR_CONSUMER_KEY`
    - `TUMBLR_CONSUMER_SECRET`
    - `TUMBLR_OAUTH_TOKEN`
    - `TUMBLR_OAUTH_SECRET`
    """

    def __init__(self, blog_name: str = "sonicocbot"):
        """Create the Tumblr poster using the environment variables described above."""
        self.__blog_name = blog_name
        self.__client: pytumblr.TumblrRestClient = pytumblr.TumblrRestClient(
            os.environ.get("TUMBLR_CONSUMER_KEY", ""),
            os.environ.get("TUMBLR_CONSUMER_SECRET", ""),
            os.environ.get("TUMBLR_OAUTH_TOKEN", ""),
            os.environ.get("TUMBLR_OAUTH_SECRET", ""),
        )

    def make_post(self, post_creator: PostCreator) -> None:
        """Make a post to Tumblr using the given `PostCreator`.

        Parameters
        ----------
        post_creator : PostCreator
            post creator to make the post
        """
        # Set post creator to prefer long text
        post_creator.prefer_long_text = True
        # Get the image and text from the post creator
        img = post_creator.get_image()
        title_txt = post_creator.get_title()
        body_txt = post_creator.get_long_text()
        # Add extra tags for Tumblr posts based on the post type
        post_tags = post_creator.get_tags()
        extra_tags: tuple[str, ...] = ("sonic", "sonic the hedgehog")
        if isinstance(post_creator, OCPostCreator):
            extra_tags += ("oc", "sonic oc", "fake oc")
        if isinstance(post_creator, TextPostCreator):
            if post_tags and "fanficbot" in post_tags:
                extra_tags += ("fanfic", "sonic fanfic", "fake fanfic")
        tags = extra_tags + (post_tags if post_tags else tuple())
        if img is None:
            self.__client.create_text(
                self.__blog_name,
                state="published",
                tags=tags,
                title=title_txt,
                body=body_txt,
                format="markdown",
            )
        else:
            with tempfile.NamedTemporaryFile(suffix=".png") as f:
                # Create a temporary file to post
                img.save(f.name, format="PNG")
                self.__client.create_photo(
                    self.__blog_name,
                    state="published",
                    tags=tags,
                    caption=body_txt,
                    format="markdown",
                    data=f.name,
                )
