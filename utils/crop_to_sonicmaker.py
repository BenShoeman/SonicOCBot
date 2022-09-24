import argparse
import glob
from pathlib import Path
from PIL import Image
from typing import Union
import yaml


def read_file(filepath: Union[str, Path]) -> str:
    with open(filepath) as f:
        return f.read()


parser = argparse.ArgumentParser()
parser.add_argument("-o", "--out-dir", default="cropped", type=str)
parser.add_argument("sonicocbotpath", metavar="sonicocbot-path", type=str)
parser.add_argument("parttype", metavar="part-type", type=str)
parser.add_argument("files", metavar="file", nargs="+", type=str)
args = parser.parse_args()

out_dir = Path(args.out_dir)
out_dir.mkdir(exist_ok=True)

sonicocbot_path = Path(args.sonicocbotpath)
sonicmaker_fill = yaml.safe_load(read_file(sonicocbot_path / "data" / "sonicmaker-fill.yml"))
part_x, part_y = sonicmaker_fill["fills"][args.parttype]["position"]
part_img = Image.open(next((sonicocbot_path / "images" / "sonicmaker").glob(f"{args.parttype}*.png")))
part_width, part_height = part_img.size

for g in args.files:
    for f in glob.glob(g):
        in_file = Path(f)
        out_file = out_dir / in_file.name
        img = Image.open(in_file).crop((part_x, part_y, part_x + part_width, part_y + part_height))
        img.save(out_file)
