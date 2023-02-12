import logging
import random
import tempfile
from typing import Literal, Optional

from src.Util.FileUtil import file_to_data_url
from src.OC import generate_oc
from src.PostCreator import *
from src.Poster import *


_logger = logging.getLogger(__name__)

_post_probabilities: dict[Literal["oc", "sonicsez", "fanfic"], float] = {
    "oc": 0.85,
    "sonicsez": 0.065,
    "fanfic": 0.085,
}


def make_post(
    post_probabilities: dict[Literal["oc", "sonicsez", "fanfic"], float] = _post_probabilities,
    dummy_post: Optional[Literal["short", "long"]] = None,
    post_type: Optional[Literal["oc", "sonicsez", "fanfic"]] = None,
    sonicmaker: bool = False,
    templated: bool = False,
    print_data_url: bool = False,
) -> None:
    """Create a post randomly based on given post probabilities.

    Parameters
    ----------
    post_probabilities : dict[Literal["oc", "sonicsez", "fanfic"], float], optional
        dict describing probabilities of each post; default values are picked if not provided
    dummy_post : Optional[Literal["short", "long"]], optional
        whether the post is a dummy post, and if so, a short or long text post, by default None
    post_type : Optional[Literal["oc", "sonicsez", "fanfic"]], optional
        which type of post to make; if omitted, uses `post_probabilities` to determine the type
    sonicmaker: bool, optional
        if True, forces an oc post to use a SonicMaker OC; by default False
    templated: bool, optional
        if True, forces an oc post to use a template OC; by default False;
        note that the `sonicmaker` argument takes precedence over this
    print_data_url: bool, optional
        if True and the post is a dummy post, prints data URL of the post image to stdout; by default False
    """
    posters: list[Poster] = []
    if dummy_post:
        posters.append(DummyPoster(prefer_long_text=(dummy_post != "short"), show_image=not print_data_url))
    else:
        # Add new social media posters to this list
        posters.extend(
            [
                TwitterPoster(),
                TumblrPoster(),
                MastodonPoster(),
                FacebookPoster(),
            ]
        )
    if post_type is None:
        post_probs = [(post, pr) for post, pr in post_probabilities.items()]
        posts = [post for post, pr in post_probs]
        probs = [pr for post, pr in post_probs]
        post_typ = random.choices(posts, probs, k=1)[0]
    else:
        post_typ = post_type

    post_creator: PostCreator
    if post_typ == "oc":
        gen_kwargs = {}
        if sonicmaker or templated:
            gen_kwargs["pr_original"] = 1.0 if sonicmaker else 0.0
        oc = generate_oc(**gen_kwargs)
        post_creator = OCHTMLPostCreator(oc=oc)
    elif post_typ == "fanfic":
        post_creator = FanficHTMLPostCreator()
    elif post_typ == "sonicsez":
        post_creator = SonicSezHTMLPostCreator()

    for poster in posters:
        curr_post_creator: PostCreator
        if isinstance(poster, (TwitterPoster, MastodonPoster)):
            # Wrap in a TwitterPostCreator to apply character limits for Twitter
            curr_post_creator = TwitterPostCreator(post_creator)
        else:
            curr_post_creator = post_creator
        _logger.info(f"Making a {post_typ} post using a {type(poster).__name__}...")
        try:
            poster.make_post(curr_post_creator)
            _logger.info("Done.")
        except Exception as e:
            _logger.error(f"{type(e).__name__} encountered in posting from {type(poster).__name__}: {e}")
        else:
            if isinstance(poster, DummyPoster) and print_data_url:
                if post_creator_img := curr_post_creator.get_image():
                    with tempfile.NamedTemporaryFile(suffix=".png") as f:
                        post_creator_img.save(f.name, format="PNG")
                        print(file_to_data_url(f.name))


def main(
    dummy_post: Optional[Literal["short", "long"]] = None,
    post_type: Optional[Literal["oc", "sonicsez", "fanfic"]] = None,
    sonicmaker: bool = False,
    templated: bool = False,
    print_data_url: bool = False,
) -> None:
    """Main app function. Parameters are same as those in `App.make_post`."""
    make_post(dummy_post=dummy_post, post_type=post_type, sonicmaker=sonicmaker, templated=templated, print_data_url=print_data_url)
