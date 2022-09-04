"""
This module defines Poster objects, which post onto various social media platforms.

The submodules are as follows:

- **src.Poster.Poster**: Has the abstract Poster class that represents a poster.
- **src.Poster.DummyPoster**: Has the Poster class that fakes creating a post by showing the PostCreator contents.
- **src.Poster.TwitterPoster**: Has the Poster class that posts onto Twitter.
- **src.Poster.TumblrPoster**: Has the Poster class that posts onto Tumblr.
"""

from .Poster import Poster
from .DummyPoster import DummyPoster
from .TwitterPoster import TwitterPoster
from .TumblrPoster import TumblrPoster
