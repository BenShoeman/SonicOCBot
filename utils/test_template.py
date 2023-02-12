from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.absolute().resolve()))

import argparse
import json
from PIL import Image, ImageDraw
import pycmarkgfm as gfm
import random
from textwrap import dedent

import src.Directories as Directories
from src.PostCreator.PostCreator import _get_font_choices
from src.Util.ColorUtil import hex2rgb, rgb2hex, contrasting_text_color
from src.Util.HTMLUtil import fill_jinja_template, html_to_image
from src.Util.ImageUtil import image_to_data_url
from src.Util.TimeUtil import get_day_state

utils_dir = Directories.PROJECT_DIR / "utils"

post_height = 680
post_width = {
    True: 907,
    False: 1200,
}
sample_palette = {
    "primary": hex2rgb("#fb0400"),
    "secondary": hex2rgb("#2548d9"),
    "tertiary": hex2rgb("#ffff00"),
}

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--type", type=str, choices=["oc", "sonicsez", "fanfic"], default="oc")
parser.add_argument("--title", type=str)
parser.add_argument("--subtitle", type=str)
parser.add_argument("--content", type=str)
parser.add_argument("--palette", type=lambda s: {k: hex2rgb(v) for k, v in json.loads(s).items()}, default="{}")
parser.add_argument("--day-state", type=str, choices=["day", "night"])
parser.add_argument("template_path", metavar="template-path", type=Path)
args = parser.parse_args()

override_args = {k: v for k, v in {"title": args.title, "subtitle": args.subtitle, "content": args.content}.items() if v}
sample_palette.update(args.palette)
font_choices = _get_font_choices(Directories.FONTS_DIR)
font_name = random.choice(list(font_choices.keys()))
regular_font_file = font_choices[font_name]["regular"]
italic_font_file = font_choices[font_name]["italic"]

if args.type == "oc":
    sample_post = {
        "title": "Sonic the Hedgehog",
        "subtitle": "he/him",
        "content": dedent(
            """
                - Age: 16
                - Height: 3 ft 4 in
                - Weight: 77 lbs
                - Traits: Laid-Back, Quick-Witted
                - Skills: Running
                - Eye Color: Green
                - Fur Color: Blue
                - Shoe Color: Red
                - Skin Color: Golden

                ---

                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce mattis massa nunc, ut imperdiet ligula porttitor ac. Pellentesque venenatis risus
                nulla, eget dapibus mi tincidunt in. Curabitur orci ex, posuere vitae leo sed, suscipit rhoncus magna lomestie. 
            """
        ).strip(),
        "image": image_to_data_url(Image.open(utils_dir / "images" / "sonic.png")),
    }
    no_text_opts = [True, False]

elif args.type == "sonicsez":
    sample_post = {
        "title": "Sonic Says...",
        "content": (
            "If there's a fire or someone's trying to break into your home, that's when you call 911. "
            "One person's dumb joke could be another person's disaster."
        ),
        "overlay": image_to_data_url(Image.open(utils_dir / "images" / "sonicsays.png")),
    }
    no_text_opts = [False]

elif args.type == "fanfic":
    sample_post = {
        "title": "Sonic Adventure (from Wikipedia)",
        "content": dedent(
            """
                When Sonic sees local police fail to defeat Chaos, he and Tails work to stop Robotnik from empowering it with the Chaos Emeralds. Knuckles, the
                only remaining echidna, sets out to find the shards of the Master Emerald and repair it.

                Robotnik activates a new series of robots, including one named Gamma, and orders them to find Froggy, an amphibian who ate a Chaos Emerald.
                Froggy's owner, Big, seeks to find him as well.
                
                In Station Square, Sonic's friend Amy finds a Flicky being pursued for a Chaos Emerald in its possession and decides to protect it. When both
                are captured, Amy convinces Gamma not to work for Robotnik; Gamma helps her to escape before seeking out and destroying the other robots in his
                series, sacrificing himself in the process. Tails, meanwhile, foils Robotnik's contingency plan to destroy Station Square via a missile strike.
            """
        ).strip(),
        "header": image_to_data_url(Image.open(utils_dir / "images" / "fanfic.png")),
    }
    no_text_opts = [False]

imgs: list[Image.Image] = []
for no_text in no_text_opts:
    template_args: dict = {
        "project_dir": str(Directories.PROJECT_DIR),
        "regular_font_path": regular_font_file,
        "italic_font_path": italic_font_file,
        "night_mode": (args.day_state if args.day_state else get_day_state()) == "night",
        "primary_color": rgb2hex(sample_palette.get("primary", (0, 0, 0))),
        "secondary_color": rgb2hex(sample_palette.get("secondary", (0, 0, 0))),
        "tertiary_color": rgb2hex(sample_palette.get("tertiary", (0, 0, 0))),
        "primary_text": rgb2hex(contrasting_text_color(sample_palette.get("primary", (0, 0, 0)))),
        "secondary_text": rgb2hex(contrasting_text_color(sample_palette.get("secondary", (0, 0, 0)))),
        "tertiary_text": rgb2hex(contrasting_text_color(sample_palette.get("tertiary", (0, 0, 0)))),
        **sample_post,
    }
    template_args["subtitle"] = template_args.get("subtitle") if not no_text else None
    template_args["content"] = gfm.gfm_to_html(template_args["content"]) if not no_text else ""
    template_args.update(override_args)
    full_html = fill_jinja_template(args.template_path, **template_args)
    imgs.append(html_to_image(full_html, width=post_width[no_text], height=post_height))

img_sizes = [img.size for img in imgs]
full_width = sum(width for width, height in img_sizes) + len(imgs) - 1
full_img: Image.Image = Image.new("RGB", size=(full_width, post_height), color="#000000")
full_img_draw: ImageDraw.ImageDraw = ImageDraw.Draw(full_img)
paste_x = 0
for img in imgs:
    if paste_x > 0:
        full_img_draw.line(((paste_x - 1, 0), (paste_x - 1, post_height - 1)), fill="#00ff00")
    full_img.paste(img, (paste_x, 0))
    paste_x += img.size[0] + 1
del full_img_draw
full_img.show()
