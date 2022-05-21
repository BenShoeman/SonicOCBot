"""
This module defines PostCreator objects, which are used to make posts for various social media platforms.

The submodules are as follows:

- **src.PostCreator.PostCreator**: Has the abstract PostCreator class that represents a post.
- **src.PostCreator.OCPostCreator**: Has the PostCreator class that creates a post involving an OC.
- **src.PostCreator.TextImagePostCreator**: Has the PostCreator class that creates a post having an image with text on it.
- **src.PostCreator.TwitterPostCreator**: Modifies a PostCreator to obey Twitter character limits.
"""

from .PostCreator import PostCreator
from .OCPostCreator import OCPostCreator
from .TextImagePostCreator import TextImagePostCreator
from .TwitterPostCreator import TwitterPostCreator
