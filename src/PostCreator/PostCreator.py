from abc import ABC, abstractmethod
from datetime import time
import glob
import json
import os
from PIL import Image
import random
from typing import Literal, Optional, Union

import src.Directories as Directories
from src.Util.ColorUtil import ColorTuple, hex_to_rgb, rgb_to_hex


def _get_font_choices(fonts_dir: str) -> dict:
    if os.path.exists(fonts_dir):
        font_names = set(
            font_file.removesuffix(".ttf").removesuffix("-Regular")
            for font_file in glob.glob(os.path.join(fonts_dir, "*.ttf"))
            if font_file.endswith(".ttf") and not font_file.endswith("-Italic.ttf")
        )
        return {
            font_name: {
                "regular": (regular_font_path := f"{font_name}.ttf" if os.path.exists(f"{font_name}.ttf") else f"{font_name}-Regular.ttf"),
                "italic": f"{font_name}-Italic.ttf" if os.path.exists(f"{font_name}-Italic.ttf") else regular_font_path,
            }
            for font_name in font_names
        }
    else:
        print(f"Error: could not load fonts as directory {fonts_dir} doesn't exist.")
        return {}


def _get_color_schedule(schedule_path: str) -> dict:
    if os.path.exists(schedule_path):
        with open(schedule_path) as f:
            schedule_dict = json.load(f)
        converted_schedule = {}
        for time_str, colors_dict in schedule_dict.items():
            hr, minute = time_str.split(":")[:2]
            time_val = time(int(hr), int(minute))
            converted_schedule[time_val] = {typ: hex_to_rgb(color) for typ, color in colors_dict.items()}
        return converted_schedule
    else:
        print(f"Error: could not load color schedule {schedule_path} as it doesn't exist. Loading fallback.")
        return {
            time(0, 0): {
                "bg": (21, 32, 43),
                "text": (255, 255, 255),
            },
            time(7, 0): {
                "bg": (255, 255, 255),
                "text": (0, 0, 0),
            },
            time(19, 0): {
                "bg": (21, 32, 43),
                "text": (255, 255, 255),
            },
        }


class PostCreator(ABC):
    """Abstract class for post creators."""

    def __init__(self, **kwargs):
        """Post creator default constructor, setting optional kwargs parameters. This should be called in subclass constructors.

        Other Parameters
        ----------------
        **kwargs : dict
            Other keyword arguments to define how the images are created. If omitted, they will get randomly populated.
            Below are the available options:
            - regular_font_file
            - italic_font_file
        """
        self.__schedule_colors = _get_color_schedule(os.path.join(Directories.DATA_DIR, "schedule-colors.json"))
        # If no font file provided, pick a random one from fonts directory
        self.regular_font_file = kwargs.get("regular_font_file")
        self.italic_font_file = kwargs.get("italic_font_file")
        if self.regular_font_file is None or self.italic_font_file is None:
            font_choices = _get_font_choices(Directories.FONTS_DIR)
            font_name = random.choice(list(font_choices.keys()))
            self.regular_font_file = self.regular_font_file or font_choices[font_name]["regular"]
            self.italic_font_file = self.italic_font_file or font_choices[font_name]["italic"]
        self._md_css: Union[str, dict] = ""
        self.__font_size = 32

    def generate_css(self, textcolor: ColorTuple) -> None:
        """Generate the CSS for images using specified font files and sizes, required whenever changing them.

        Parameters
        ----------
        textcolor : ColorTuple
            3-tuple of colors in RGB, in interval [0, 255]
        """
        # Create CSS for images
        self._md_css = {
            "@font-face": [
                {
                    "font-family": "customfont",
                    "src": f"url('file://{self.regular_font_file}')",
                },
            ],
            "*": {
                "background-color": "transparent",
                "font-family": "customfont",
                "color": rgb_to_hex(textcolor),
                "font-size": f"{self.__font_size}px",
            },
            "h1, p, ul, ol": {
                "margin": "0.5em 0 0.5em 0",
            },
            "h1": {
                "font-size": "1.5em",
            },
            "hr": {
                "border": f"1px solid {rgb_to_hex(textcolor)}",
                "opacity": "0.375",
                "margin": "0.75em",
            },
            ".small": {
                "font-size": "0.75em",
                "font-style": "normal",
                "font-weight": "normal",
            },
            "em, i": {
                "font-family": "customfontitalic, customfont",
            },
        }
        if self.italic_font_file != self.regular_font_file:
            self._md_css["@font-face"].append(
                {
                    "font-family": "customfontitalic",
                    "src": f"url('file://{self.italic_font_file}')",
                }
            )

    def set_font_size(self, font_size: int = 32) -> None:
        """Set a font size for the text image.

        Parameters
        ----------
        font_size : int, optional
            font size for the image, by default 32
        """
        self.__font_size = font_size

    def __get_schedule_color_for_time(self, typ: Literal["bg", "text"], current_time: time) -> ColorTuple:
        """Return background color ("bg") or text color ("text") based on the schedule.

        Parameters
        ----------
        typ : Literal["bg", "text"]
            whether to get the background ("bg") or text ("text") color.
        current_time : time
            current time

        Returns
        -------
        ColorTuple
            3-tuple of colors in RGB, in interval [0, 255]
        """
        schedule = sorted(self.__schedule_colors.items(), key=lambda item: item[0], reverse=True)
        # Check times in reverse order to find whether the time lies in the specific time range
        for time_val, colors_dict in schedule:
            if current_time >= time_val:
                return colors_dict.get(typ, (0, 0, 0))
        # Fall back to last value in schedule, in case early time was omitted
        time_val, colors_dict = schedule[0]
        return colors_dict.get(typ, (0, 0, 0))

    def _get_bgcolor_for_time(self, current_time: time) -> ColorTuple:
        """Return background color based on the schedule.

        Parameters
        ----------
        current_time : time
            current time

        Returns
        -------
        ColorTuple
            3-tuple of colors in RGB, in interval [0, 255]
        """
        return self.__get_schedule_color_for_time("bg", current_time)

    def _get_textcolor_for_time(self, current_time: time) -> ColorTuple:
        """Return text color based on the schedule.

        Parameters
        ----------
        current_time : time
            current time

        Returns
        -------
        ColorTuple
            3-tuple of colors in RGB, in interval [0, 255]
        """
        return self.__get_schedule_color_for_time("text", current_time)

    @abstractmethod
    def get_image(self) -> Optional[Image.Image]:
        """Returns the image for the post, if there is one.

        Returns
        -------
        Optional[Image.Image]
            image of the post, or None if no image
        """

    @abstractmethod
    def get_alt_text(self) -> Optional[str]:
        """Returns alt text for the post image, if there is alt text.

        Returns
        -------
        Optional[str]
            alt text for the post's image, or None if there is none
        """

    @abstractmethod
    def get_text(self) -> str:
        """Returns the text for the post.

        Returns
        -------
        str
            text of the post
        """