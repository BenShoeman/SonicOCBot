import base64
import io
import json
from PIL import Image

class BitmapFont:
    def __init__(self, json_filename):
        font_data = json.load(open(json_filename))
        self.name = font_data["font_name"]
        self.char_loc = font_data["char_loc"]
        self.char_height = font_data["char_height"]
        # Decode base64-encoded png image in json file
        img_bytes = base64.b64decode(font_data["image"].encode("ascii"))
        self.image = Image.open(io.BytesIO(img_bytes))
    
    def get_string_width(self, string):
        # Sum up all character widths, but use a space if char. not recognized
        return sum(
            self.char_loc[c]["width"] if c in self.char_loc
            else self.char_loc[' ']["width"] for c in string
        )
    
    def get_character(self, character):
        # Return an empty space if character not recognized
        if character not in self.char_loc:
            return Image.new("RGBA", (self.char_loc[' ']["width"], self.char_height))
        char_loc = self.char_loc[character]
        return self.image.crop((
            char_loc["x"], 0, char_loc["x"] + char_loc["width"], self.char_height
        ))
    
    def get_word(self, word):
        word_img = Image.new("RGBA", (self.get_string_width(word), self.char_height))
        space_width = self.char_loc[' ']["width"]
        x_pos = 0
        for c in word:
            word_img.paste(self.get_character(c), (x_pos, 0))
            x_pos += self.char_loc[c]["width"] if c in self.char_loc else space_width
        return word_img
    
    def get_text(self, string, width=490, line_padding=2):
        if len(string.strip()) == 0:
            raise Exception("String must be non-empty.")
        # Build lines. Keep adding words to a line until it exceeds width
        lines = []
        linebreak_queue = string.split('\n')
        while len(linebreak_queue) > 0:
            substring = linebreak_queue.pop(0)
            word_queue = substring.split(' ')
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
        text_img = Image.new("RGBA", (width, (self.char_height+line_padding)*len(lines)-line_padding))
        space_width = self.char_loc[' ']["width"]
        x_pos = 0
        y_pos = 0
        for line in lines:
            for c in line:
                if c != ' ':
                    text_img.paste(self.get_character(c), (x_pos, y_pos))
                x_pos += self.char_loc[c]["width"] if c in self.char_loc else space_width
            x_pos = 0
            y_pos += self.char_height + line_padding
        return text_img