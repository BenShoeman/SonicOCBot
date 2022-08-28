import glob
import os
import random
from typing import Literal, Optional

import src.Directories as Directories
from src.OC import generate_oc
from src.PostCreator import PostCreator, OCPostCreator, TextImagePostCreator, TwitterPostCreator
from src.FanfictionGenerator import TwitterFanfictionGenerator
from src.SonicSezGenerator import SonicSezGenerator
from src.Poster import DummyPoster, TwitterPoster
from src.TextModel import RNNTextModel


_ffic_generator = TwitterFanfictionGenerator(body_text_model_name="fanfics.bodies", titles_model_name="fanfics.titles", model_class=RNNTextModel)
_ssez_generator = SonicSezGenerator(body_text_model_name="sonicsez", model_class=RNNTextModel)

_ffic_logo_images = glob.glob(os.path.join(Directories.IMAGES_DIR, "fanficlogo", "*.png"))
_ssez_bg_images = glob.glob(os.path.join(Directories.IMAGES_DIR, "sonicsez", "*.png"))

_post_probabilities: dict[Literal["oc", "sonicsez", "fanfic"], float] = {
    "oc": 0.85,
    "sonicsez": 0.075,
    "fanfic": 0.075,
}


def make_post(
    post_probabilities: dict[Literal["oc", "sonicsez", "fanfic"], float] = _post_probabilities,
    dummy_post: bool = False,
    post_type: Optional[Literal["oc", "sonicsez", "fanfic"]] = None,
    sonicmaker: bool = False,
    templated: bool = False,
) -> None:
    """Create a post randomly based on given post probabilities.

    Parameters
    ----------
    post_probabilities : dict[Literal["oc", "sonicsez", "fanfic"], float], optional
        dict describing probabilities of each post; default values are picked if not provided
    dummy_post : bool, optional
        whether the post is a dummy post, by default False
    post_type : Optional[Literal["oc", "sonicsez", "fanfic"]], optional
        which type of post to make; if omitted, uses `post_probabilities` to determine the type
    sonicmaker: bool, optional
        if True, forces an oc post to use a SonicMaker OC; by default False
    templated: bool, optional
        if True, forces an oc post to use a template OC; by default False
        note that the `sonicmaker` argument takes precedence over this
    """
    poster = DummyPoster() if dummy_post else TwitterPoster()
    if post_type is None:
        post_probs = [(post, pr) for post, pr in post_probabilities.items()]
        posts = [post for post, pr in post_probs]
        probs = [pr for post, pr in post_probs]
        post_typ = random.choices(posts, probs, k=1)[0]
    else:
        post_typ = post_type

    post_creator: PostCreator
    if post_typ == "fanfic":
        title, text = _ffic_generator.get_fanfiction()
        post_creator = TextImagePostCreator(text=text, title=title, tags=("#ocbot", "#fanficbot"))
        if len(_ffic_logo_images) > 0:
            post_creator.set_banner(random.choices(_ffic_logo_images, k=1)[0])
    elif post_typ == "sonicsez":
        text = _ssez_generator.get_text()
        post_creator = TextImagePostCreator(text=text)
        post_creator.set_font_size(64)
        if len(_ssez_bg_images) > 0:
            post_creator.set_overlay(random.choices(_ssez_bg_images, k=1)[0], alpha=56)
    else:
        if not (sonicmaker or templated):
            oc = generate_oc()
        elif sonicmaker:
            oc = generate_oc(pr_original=1.0)
        else:
            oc = generate_oc(pr_original=0.0)
        post_creator = OCPostCreator(oc=oc)
    # Wrap in a TwitterPostCreator to apply character limits
    post_creator = TwitterPostCreator(post_creator)
    print(f"Making a {post_typ} post... ", end="")
    poster.make_post(post_creator)
    print("Done.")


def main(
    dummy_post: bool = False,
    post_type: Optional[Literal["oc", "sonicsez", "fanfic"]] = None,
    sonicmaker: bool = False,
    templated: bool = False,
):
    """Main app function. Parameters are same as those in `App.make_post`."""
    make_post(dummy_post=dummy_post, post_type=post_type, sonicmaker=sonicmaker, templated=templated)
