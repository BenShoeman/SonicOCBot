import base64
import io
import json
from os import PathLike
from PIL import Image
from typing import Union


class BitmapFont:
    """A font using a raster image.

    Parameters
    ----------
    json_filename : str
        JSON file path that includes font information. This includes the following keys in an object:
        - `"font_name"`: The name of the font (currently unused)
        - `"char_loc"`: Character x-position in the image
        - `"char_height"`: Height of the image. May stop using in favor of just using the image height
        - `"image"`: Image of the characters, base64 encoded
    """

    def __init__(self, json_filename: Union[str, PathLike]):
        font_data = json.load(open(json_filename))
        self.name = font_data["font_name"]
        self.char_loc = font_data["char_loc"]
        self.char_height = font_data["char_height"]
        # Decode base64-encoded png image in json file
        img_bytes = base64.b64decode(font_data["image"].encode("ascii"))
        self.image = Image.open(io.BytesIO(img_bytes))

    def get_string_width(self, string: str) -> int:
        """Returns width of a string using this font.

        Parameters
        ----------
        string : str
            string to get width of

        Returns
        -------
        int
            width of the string in pixels
        """

        # Sum up all character widths, but use a space if char. not recognized
        return sum(self.char_loc[c]["width"] if c in self.char_loc else self.char_loc[" "]["width"] for c in string)

    def get_character(self, character: str) -> Image.Image:
        """Returns image of the character with this font.

        Parameters
        ----------
        character : str
            character to get image of

        Returns
        -------
        PIL.Image
            image of the character
        """

        # Return an empty space if character not recognized
        if character not in self.char_loc:
            return Image.new("RGBA", (self.char_loc[" "]["width"], self.char_height))
        char_loc = self.char_loc[character]
        return self.image.crop((char_loc["x"], 0, char_loc["x"] + char_loc["width"], self.char_height))

    def get_word(self, word: str) -> Image.Image:
        """Returns image of the word with this font.

        Parameters
        ----------
        word : str
            word to get image of

        Returns
        -------
        PIL.Image
            image of the word
        """

        word_img = Image.new("RGBA", (self.get_string_width(word), self.char_height))
        space_width = self.char_loc[" "]["width"]
        x_pos = 0
        for c in word:
            word_img.paste(self.get_character(c), (x_pos, 0))
            x_pos += self.char_loc[c]["width"] if c in self.char_loc else space_width
        return word_img

    def get_text(self, string: str, width: int = 490, line_padding: int = 2) -> Image.Image:
        """Returns image of the string with this font.

        Parameters
        ----------
        string : str
            string to get image of
        width : int, optional
            max width of each line in pixels, by default 490
        line_padding : int, optional
            spacing between each line in pixels, by default 2

        Returns
        -------
        PIL.Image
            image of the string

        Raises
        ------
        Exception
            if the string is empty
        """

        if len(string.strip()) == 0:
            raise Exception("String must be non-empty.")
        # Build lines. Keep adding words to a line until it exceeds width
        lines = []
        linebreak_queue = string.split("\n")
        while len(linebreak_queue) > 0:
            substring = linebreak_queue.pop(0)
            word_queue = substring.split(" ")
            curr_line = word_queue.pop(0)
            while len(word_queue) > 0:
                curr_word = word_queue.pop(0)
                if self.get_string_width(curr_line + " " + curr_word) <= width:
                    curr_line += " " + curr_word
                else:
                    lines.append(curr_line)
                    word_queue.insert(0, curr_word)
                    if len(word_queue) > 0:
                        curr_line = word_queue.pop(0)
            # If we didn't just append the current line, append it
            if len(lines) == 0 or curr_line != lines[-1]:
                lines.append(curr_line)

        # Create the image now
        text_img = Image.new("RGBA", (width, (self.char_height + line_padding) * len(lines) - line_padding))
        space_width = self.char_loc[" "]["width"]
        x_pos = 0
        y_pos = 0
        for line in lines:
            for c in line:
                if c != " ":
                    text_img.paste(self.get_character(c), (x_pos, y_pos))
                x_pos += self.char_loc[c]["width"] if c in self.char_loc else space_width
            x_pos = 0
            y_pos += self.char_height + line_padding
        return text_img
