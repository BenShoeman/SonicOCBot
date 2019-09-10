import base64
from io import BytesIO
import json
import os
from PIL import Image, ImageDraw, ImageFont
import sys

# Need to import BitmapFont from parent directory
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
from BitmapFont import BitmapFont

FONT_STRING = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()-=[]\\;',./_+{}|:\"<>?"

def main():
    if len(sys.argv) not in [3,4,5]:
        print(f"Usage: {sys.argv[0]} <font filename> <font size> <font name:optional> <color:optional>")
        sys.exit(1)

    imfont = ImageFont.truetype(sys.argv[1], size=int(sys.argv[2]))
    imfont_color = "black" if len(sys.argv) < 5 else sys.argv[4]
    # Get initial size estimate; may be wrong, but this is to create the image
    init_width, init_height = imfont.getsize(FONT_STRING)

    # Initialize the dictionary structure
    font_dict = {}
    if len(sys.argv) < 4:
        font_dict["font_name"] = sys.argv[1]
    else:
        font_dict["font_name"] = sys.argv[3]
    font_dict["char_loc"] = {" ": {"width": imfont.getsize(" ")[0]}}
    font_dict["char_height"] = init_height

    # Initialize image and add characters sequentially to the font string, while updating font_dict
    font_img = Image.new("RGBA", (init_width, init_height), (0,0,0,0))
    x = 0
    for c in FONT_STRING:
        # Get character dimensions so it can be placed correctly
        char_width, char_height = imfont.getsize(c)

        # If the character will go beyond the image bounds, resize the image
        if x + char_width > font_img.size[0]:
            new_img = Image.new("RGBA", (x + char_width, init_height))
            new_img.paste(font_img)
            del font_img
            font_img = new_img

        char_img = Image.new("RGBA", (char_width, char_height))
        ImageDraw.Draw(char_img).text((0,0), c, imfont_color, imfont)
        font_img.paste(char_img, (x,0))
        del char_img

        # Update the font_dict so we capture this info, then update the x-position
        font_dict["char_loc"][c] = {"x": x, "width": char_width}
        x += char_width

    # Add the base64 string encoding of the image to the dict
    fp = BytesIO()
    font_img.save(fp, format="png")
    fp.seek(0) # Go back to beginning of file to re-read saved image
    font_dict["image"] = str(base64.b64encode(fp.read()), encoding="ascii")

    # Save file to font filename .json
    new_fname = f"{font_dict['font_name']}-{sys.argv[2]}" + ("" if len(sys.argv) < 5 else "-"+sys.argv[4]) + ".json"
    json.dump(font_dict, open(new_fname, 'w'))

    # Show an image preview
    new_font = BitmapFont(new_fname)
    txt_img = new_font.get_text("the quick brown fox jumps over the lazy dog. SPHINX OF BLACK QUARTZ, JUDGE MY VOW!\n"
        + FONT_STRING, width=font_img.size[0])
    preview_img = Image.new("RGB", txt_img.size, color="black" if imfont_color.lower() in ["white","#ffffff"] else "white")
    preview_img.paste(txt_img, txt_img)
    preview_img.show()

if __name__ == "__main__":
    main()