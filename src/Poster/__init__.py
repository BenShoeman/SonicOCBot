"""
This module defines Poster objects, which post onto various social media platforms.

The submodules are as follows:

- **src.Poster.Poster**: Has the abstract Poster class that represents a poster.
- **src.Poster.DummyPoster**: Has the Poster class that fakes creating a post by showing the PostCreator contents.
- **src.Poster.FacebookPoster**: Has the Poster class that posts onto Facebook.
- **src.Poster.InstagramPoster**: Has the Poster class that posts onto Instagram.
- **src.Poster.MastodonPoster**: Has the Poster class that posts onto Mastodon.
- **src.Poster.TwitterPoster**: Has the Poster class that posts onto Twitter.
- **src.Poster.TumblrPoster**: Has the Poster class that posts onto Tumblr.
"""

from .Poster import Poster
from .DummyPoster import DummyPoster
from .FacebookPoster import FacebookPoster
from .InstagramPoster import InstagramPoster
from .MastodonPoster import MastodonPoster
from .TwitterPoster import TwitterPoster
from .TumblrPoster import TumblrPoster
