from abc import ABC, abstractmethod
import datetime

from BitmapFont import *
import Directories

class PostCreator(ABC):
    __DEFAULT_KWARGS = {
        "lightmode_bg": (255, 255, 255),
        "darkmode_bg": (21, 32, 43),
        "lightmode_font": BitmapFont(f"{Directories.FONTS_DIR}/defaultsanslight.json"),
        "darkmode_font": BitmapFont(f"{Directories.FONTS_DIR}/defaultsansdark.json")
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