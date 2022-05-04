from abc import ABC, abstractmethod

from src.PostCreator.PostCreator import PostCreator


class Poster(ABC):
    """Interface for posters. Must implement `make_post`."""

    @abstractmethod
    def make_post(self, post_creator: PostCreator) -> None:
        """Make a post using the given `PostCreator`.

        Parameters
        ----------
        post_creator : PostCreator
            post creator to make the post
        """
