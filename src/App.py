import random
from typing import Literal, Optional

import src.Directories as Directories
from src.OC import generate_oc
from src.PostCreator import PostCreator, OCPostCreator, TextPostCreator, HTMLPostCreator, OCHTMLPostCreator, TwitterPostCreator
from src.FanfictionGenerator import TwitterFanfictionGenerator
from src.SonicSezGenerator import SonicSezGenerator
from src.Poster import Poster, DummyPoster, TwitterPoster, TumblrPoster
from src.TextModel import MarkovTextModel


_ffic_generator = TwitterFanfictionGenerator(body_text_model_name="fanfics.bodies", titles_model_name="fanfics.titles", model_class=MarkovTextModel)
_ssez_generator = SonicSezGenerator(body_text_model_name="sonicsez", model_class=MarkovTextModel)

_ffic_logo_images = list((Directories.IMAGES_DIR / "fanficlogo").glob("*.png"))
_ssez_bg_images = list((Directories.IMAGES_DIR / "sonicsez").glob("*.png"))

_post_probabilities: dict[Literal["oc", "sonicsez", "fanfic"], float] = {
    "oc": 0.85,
    "sonicsez": 0.075,
    "fanfic": 0.075,
}


def make_post(
    post_probabilities: dict[Literal["oc", "sonicsez", "fanfic"], float] = _post_probabilities,
    dummy_post: Optional[Literal["short", "long"]] = None,
    post_type: Optional[Literal["oc", "sonicsez", "fanfic"]] = None,
    sonicmaker: bool = False,
    templated: bool = False,
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
    """
    posters: list[Poster] = [DummyPoster(prefer_long_text=(dummy_post != "short"))] if dummy_post else [TwitterPoster(), TumblrPoster()]
    if post_type is None:
        post_probs = [(post, pr) for post, pr in post_probabilities.items()]
        posts = [post for post, pr in post_probs]
        probs = [pr for post, pr in post_probs]
        post_typ = random.choices(posts, probs, k=1)[0]
    else:
        post_typ = post_type

    use_stylized = random.random() <= 0.5  # Whether to use a stylized HTML post from /templates
    post_creator: PostCreator
    if post_typ == "fanfic":
        title, text = _ffic_generator.get_fanfiction()
        if use_stylized:
            post_creator = HTMLPostCreator(content=text, title=title, tags=("fanfic bot",))
        else:
            post_creator = TextPostCreator(content=text, title=title, tags=("fanfic bot",))
            if len(_ffic_logo_images) > 0:
                post_creator.set_banner(random.choice(_ffic_logo_images))
    elif post_typ == "sonicsez":
        text = _ssez_generator.get_text()
        if use_stylized:
            post_creator = HTMLPostCreator(content=text, title="Sonic Says...", tags=("sonic says", "sonic sez"))
        else:
            post_creator = TextPostCreator(content=text, title="Sonic Says...", tags=("sonic says", "sonic sez"))
            post_creator.set_font_size(64)
            if len(_ssez_bg_images) > 0:
                post_creator.set_overlay(random.choice(_ssez_bg_images), alpha=56)
    else:
        if not (sonicmaker or templated):
            oc = generate_oc()
        elif sonicmaker:
            oc = generate_oc(pr_original=1.0)
        else:
            oc = generate_oc(pr_original=0.0)
        if use_stylized:
            post_creator = OCHTMLPostCreator(oc=oc)
        else:
            post_creator = OCPostCreator(oc=oc)

    for poster in posters:
        poster_typ = type(poster)
        curr_post_creator: PostCreator
        if poster_typ == TwitterPoster:
            # Wrap in a TwitterPostCreator to apply character limits for Twitter
            curr_post_creator = TwitterPostCreator(post_creator)
        else:
            curr_post_creator = post_creator
        print(f"Making a {post_typ} post using a {poster_typ.__name__}... ", end="")
        try:
            poster.make_post(curr_post_creator)
            print("Done.")
        except Exception as e:
            print(f"{type(e).__name__} encountered in posting from {poster_typ.__name__}: {e}")


def main(
    dummy_post: Optional[Literal["short", "long"]] = None,
    post_type: Optional[Literal["oc", "sonicsez", "fanfic"]] = None,
    sonicmaker: bool = False,
    templated: bool = False,
) -> None:
    """Main app function. Parameters are same as those in `App.make_post`."""
    make_post(dummy_post=dummy_post, post_type=post_type, sonicmaker=sonicmaker, templated=templated)
