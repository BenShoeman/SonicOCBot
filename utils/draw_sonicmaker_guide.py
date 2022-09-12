import argparse
import glob
from PIL import Image, ImageDraw
from pathlib import Path
from typing import Union
import yaml


def read_file(filepath: Union[str, Path]) -> str:
    with open(filepath) as f:
        return f.read()


parser = argparse.ArgumentParser()
parser.add_argument("-o", "--out-dir", default=".", type=str)
parser.add_argument("sonicocbotpath", metavar="sonicocbot-path", type=str)
args = parser.parse_args()

sonicocbot_path = Path(args.sonicocbotpath)
sonicmaker_fill = yaml.safe_load(read_file(sonicocbot_path / "data" / "sonicmaker-fill.yml"))
colors = ["black", "red", "orange", "gold", "limegreen", "green", "darkcyan", "blue", "blueviolet", "magenta", "deeppink"]

template = Image.new("RGB", sonicmaker_fill["image-size"], "#ffffff")
tmpldraw = ImageDraw.Draw(template)

for i, (part_name, part_fill) in enumerate(((k, v) for k, v in sonicmaker_fill.get("fills", {}).items())):
    part_img = Image.open(glob.glob(str(sonicocbot_path / "images" / "sonicmaker" / f"{part_name}*.png"))[0])
    part_x, part_y = part_fill["position"]
    part_width, part_height = part_img.size
    tmpldraw.rectangle((part_x, part_y, part_x + part_width - 1, part_y + part_height - 1), None, colors[i])
    tmpldraw.text((part_x + 5, part_y + 5), part_name, colors[i])

template.save(Path(args.out_dir) / "template.png")
