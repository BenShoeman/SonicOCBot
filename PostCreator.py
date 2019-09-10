from abc import ABC, abstractmethod
import datetime
import json
import os
import random

from BitmapFont import *
import Directories

class PostCreator(ABC):
    __FONT_PREFS = json.load(open(os.path.join(Directories.FONTS_DIR, "font-prefs.json")))

    __DEFAULT_KWARGS = {
        "lightmode_bg": (255, 255, 255),
        "darkmode_bg": (21, 32, 43),
    }

    def __time_in_range(time, start, end):
        if start <= end:
            return start <= time <= end
        else:
            return start <= time or time <= end

    def __init__(self, **kwargs):
        self.__kwargs = {}
        for k in PostCreator.__DEFAULT_KWARGS:
            self.__kwargs[k] = kwargs.get(k, PostCreator.__DEFAULT_KWARGS[k])
        # Get a random light mode and dark mode font if not given
        if "lightmode_font" not in self.__kwargs:
            n = random.random()
            for fname, pr in PostCreator.__FONT_PREFS["light_probability"].items():
                if n < pr:
                    break
                n -= pr
            self.__kwargs["lightmode_font"] = BitmapFont(os.path.join(Directories.FONTS_DIR, fname))
        if "darkmode_font" not in self.__kwargs:
            n = random.random()
            for fname, pr in PostCreator.__FONT_PREFS["dark_probability"].items():
                if n < pr:
                    break
                n -= pr
            self.__kwargs["darkmode_font"] = BitmapFont(os.path.join(Directories.FONTS_DIR, fname))
    
    # Returns dark mode BG from 7:00PM-6:59AM, light mode otherwise.
    def _get_bgcolor_for_time(self, time):
        if PostCreator.__time_in_range(
            time, datetime.time(19,0,0), datetime.time(6,59,59)
        ):
            return self.__kwargs["darkmode_bg"]
        else:
            return self.__kwargs["lightmode_bg"]
    
    # Returns dark mode font from 7:00PM-6:59AM, light mode otherwise.
    def _get_font_for_time(self, time):
        if PostCreator.__time_in_range(
            time, datetime.time(19,0,0), datetime.time(6,59,59)
        ):
            return self.__kwargs["darkmode_font"]
        else:
            return self.__kwargs["lightmode_font"]
    
    # Should return a PIL image or None.
    @abstractmethod
    def get_image(self):
        pass
    
    # Should return text.
    @abstractmethod
    def get_text(self):
        pass