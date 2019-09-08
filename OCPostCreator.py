import datetime
from PIL import Image

from PostCreator import *

class OCPostCreator(PostCreator):
    def __init__(self, oc, **kwargs):
        self.__oc = oc
        super().__init__(**kwargs)
    
    def get_image(self):
        current_time = datetime.datetime.now().time()
        oc_img = self.__oc.image
        width, height = oc_img.size
        post_img = Image.new(
            "RGB", (int((height if height > width else width)*1.78)+5, height),
            self._get_bgcolor_for_time(current_time)
        )
        post_width, post_height = post_img.size
        post_img.paste(oc_img, (0,0), oc_img)
        font = self._get_font_for_time(current_time)
        text_img = font.get_text(self.__get_oc_text(), post_width-width-15)
        # Squish text_img to fit height if it exceeds height
        ti_width, ti_height = text_img.size
        if ti_height > height - 20:
            text_img = text_img.resize((ti_width, height-20), Image.BICUBIC)
        post_img.paste(text_img, (width+5, height//2-text_img.size[1]//2), text_img)
        return post_img
    
    def get_text(self):
        oc = self.__oc
        post_text = oc.name + " the " + oc.species.title() + " #sonicoc #bot"
        return post_text
    
    def __get_oc_text(self):
        oc = self.__oc
        post_text = oc.name + " the " + oc.species.title() + "\n\n"
        post_text += f"Age: {oc.age}\nGender: {oc.gender.title()}\n"
        post_text += f"Personality: {oc.personality.title()}\n"
        post_text += f"Height: {oc.height}\n"
        post_text += f"Weight: {oc.weight}\n"
        post_text += f"Skills: {', '.join(oc.skills).title()}\n"
        for k in sorted(oc.color_regions.keys()):
            post_text += f"{k.title()} Color: {oc.color_regions[k].title()}\n"
        post_text += f"\n{oc.description}"
        return post_text