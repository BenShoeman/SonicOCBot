"""
This module defines PostCreator objects, which are used to make posts for various social media platforms.

The submodules are as follows:

- **src.PostCreator.PostCreator**: Abstract PostCreator class that represents a post.
- **src.PostCreator.HTMLPostCreator**: PostCreator class that creates a post using HTML and Jinja2 templating for the image.
- **src.PostCreator.OCHTMLPostCreator**: HTMLPostCreator subclass that creates a post involving an OC.
- **src.PostCreator.FanficHTMLPostCreator**: HTMLPostCreator subclass that creates a post using a generator for fanfics.
- **src.PostCreator.SonicSezHTMLPostCreator**: HTMLPostCreator subclass that creates a post using a generator for Sonic Sez segments.
- **src.PostCreator.TwitterPostCreator**: PostCreator wrapper that modifies the PostCreator to obey Twitter character limits.
"""

from .PostCreator import PostCreator
from .HTMLPostCreator import HTMLPostCreator
from .OCHTMLPostCreator import OCHTMLPostCreator
from .FanficHTMLPostCreator import FanficHTMLPostCreator
from .SonicSezHTMLPostCreator import SonicSezHTMLPostCreator
from .TwitterPostCreator import TwitterPostCreator
