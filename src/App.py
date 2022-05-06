import glob
import os
import random

import src.Directories as Directories
from src.OC import generate_oc
from src.PostCreator.PostCreator import PostCreator
from src.PostCreator.OCPostCreator import OCPostCreator
from src.PostCreator.TextImagePostCreator import TextImagePostCreator
from src.FanfictionGenerator import TwitterFanfictionGenerator
from src.SonicSezGenerator import SonicSezGenerator
from src.Poster.DummyPoster import DummyPoster
from src.Poster.TwitterPoster import TwitterPoster
from src.TextModel.RNNTextModel import RNNTextModel


ffic_generator = TwitterFanfictionGenerator(body_text_model_name="fanfics.bodies", titles_model_name="fanfics.titles", model_class=RNNTextModel)
ssez_generator = SonicSezGenerator(body_text_model_name="sonicsez", model_class=RNNTextModel)

ffic_logo_images = glob.glob(os.path.join(Directories.IMAGES_DIR, "fanficlogo", "*.png"))
ssez_bg_images = glob.glob(os.path.join(Directories.IMAGES_DIR, "sonicsez", "*.png"))

post_probabilities = {
    "oc": 0.85,
    "sonicsez": 0.075,
    "fanfic": 0.075,
}


def make_post(post_probabilities: dict[str, float] = post_probabilities, dummy_post: bool = False) -> None:
    poster = DummyPoster() if dummy_post else TwitterPoster()
    post_probs = [(post, pr) for post, pr in post_probabilities.items()]
    posts = [post for post, pr in post_probs]
    probs = [pr for post, pr in post_probs]
    post_typ = random.choices(posts, probs, k=1)[0]

    post_creator: PostCreator
    if post_typ == "fanfic":
        title, text = ffic_generator.get_fanfiction()
        post_creator = TextImagePostCreator(text=text, title=title, tags=("#ocbot", "#fanficbot"))
        if len(ffic_logo_images) > 0:
            post_creator.set_banner(random.choices(ffic_logo_images, k=1)[0])
    elif post_typ == "sonicsez":
        text = ssez_generator.get_text()
        post_creator = TextImagePostCreator(text=text)
        post_creator.set_font_size(64)
        if len(ssez_bg_images) > 0:
            post_creator.set_overlay(random.choices(ssez_bg_images, k=1)[0], alpha=56)
    else:
        oc = generate_oc()
        post_creator = OCPostCreator(oc=oc)
    print(f"Making a {post_typ} post... ", end="")
    poster.make_post(post_creator)
    print("Done.")


def main(dummy_post: bool = False):
    make_post(dummy_post=dummy_post)
