from concurrent.futures import ThreadPoolExecutor
import logging
import random
import tempfile
import traceback
from typing import Literal, Optional

from src.Util.FileUtil import file_to_data_url
from src.OC import generate_oc
from src.PostCreator import *
from src.Poster import *


_logger = logging.getLogger(__name__)

_post_probabilities: dict[Literal["oc", "sonicsez", "fanfic"], float] = {
    "oc": 0.84,
    "sonicsez": 0.07,
    "fanfic": 0.09,
}


def do_posts(
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
                InstagramPoster(),
            ]
        )

    # Submit requests for posters in threads since APIs can be laggy
    with ThreadPoolExecutor(max_workers=5) as executor:
        for poster in posters:
            executor.submit(
                make_post,
                poster=poster,
                post_probabilities=post_probabilities,
                post_type=post_type,
                sonicmaker=sonicmaker,
                templated=templated,
                print_data_url=print_data_url,
            )


def make_post(
    poster: Poster,
    post_probabilities: dict[Literal["oc", "sonicsez", "fanfic"], float] = _post_probabilities,
    post_type: Optional[Literal["oc", "sonicsez", "fanfic"]] = None,
    sonicmaker: bool = False,
    templated: bool = False,
    print_data_url: bool = False,
) -> None:
    """Actually make the post using the inputted poster.

    Has most of the same parameters as `do_posts` (except `dummy_post`) along with an additional one:

    Parameters
    ----------
    poster : Poster
        the service to post to
    """
    if post_type is None:
        post_probs = [(post, pr) for post, pr in post_probabilities.items()]
        posts = [post for post, pr in post_probs]
        probs = [pr for post, pr in post_probs]
        selected_post_type = random.choices(posts, probs, k=1)[0]
    else:
        selected_post_type = post_type
    _logger.info(f"{type(poster).__name__}: making a {selected_post_type} post...")

    post_creator: PostCreator
    if selected_post_type == "oc":
        gen_kwargs = {}
        if sonicmaker or templated:
            gen_kwargs["pr_original"] = 1.0 if sonicmaker else 0.0
        oc = generate_oc(**gen_kwargs)
        post_creator = OCHTMLPostCreator(oc=oc)
    elif selected_post_type == "fanfic":
        post_creator = FanficHTMLPostCreator()
    elif selected_post_type == "sonicsez":
        post_creator = SonicSezHTMLPostCreator()

    curr_post_creator: PostCreator
    if isinstance(poster, (TwitterPoster, MastodonPoster)):
        # Wrap in a TwitterPostCreator to apply character limits for Twitter
        curr_post_creator = TwitterPostCreator(post_creator)
    else:
        curr_post_creator = post_creator
    try:
        poster.make_post(curr_post_creator)
        _logger.info(f"{type(poster).__name__}: Done posting.")
    except Exception as e:
        _logger.error(f"{type(poster).__name__}: {type(e).__name__} encountered.\n{traceback.format_exc()}")
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
    do_posts(dummy_post=dummy_post, post_type=post_type, sonicmaker=sonicmaker, templated=templated, print_data_url=print_data_url)
