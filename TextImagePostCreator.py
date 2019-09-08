import datetime
from PIL import Image

from PostCreator import *

class TextImagePostCreator(PostCreator):
    # Tags is a list or tuple of hashtags (be sure to include the pound sign)
    def __init__(self, text, title=None, tags=None, **kwargs):
        self.__text = text
        self.__title = title
        self.__tags = tags
        super().__init__(**kwargs)
    
    def get_image(self):
        current_time = datetime.datetime.now().time()
        img_width, img_height = 700, 420
        post_img = Image.new(
            "RGB", (img_width, img_height),
            self._get_bgcolor_for_time(current_time)
        )
        font = self._get_font_for_time(current_time)
        post_text = (
            (self.__title + "\n\n" if self.__title is not None else "") +
            self.__text
        )
        text_img = font.get_text(post_text, img_width-20)
        # Squish text_img to fit height if it exceeds height
        ti_width, ti_height = text_img.size
        if ti_height > img_height - 20:
            text_img = text_img.resize((ti_width, img_height-20), Image.BICUBIC)
        post_img.paste(text_img, (10, img_height//2-text_img.size[1]//2), text_img)
        return post_img
    
    def get_text(self):
        content = self.__title
        if content is None:
            # Get first five words from text then add ellipsis
            content_words = self.__text.split(None, 5)
            content = ' '.join(content_words[:-1]) + "..."
        # Then add hashtags
        if self.__tags is not None:
            content += ' ' + ' '.join(self.__tags)
        return content