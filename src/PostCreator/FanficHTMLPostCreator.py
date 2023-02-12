import logging
from pathlib import Path
import random
from requests import HTTPError
from typing import Any, ClassVar, List, Optional, Union

from .HTMLPostCreator import HTMLPostCreator
import src.Directories as Directories
from src.TextGenerator import TextGenerator, FanfictionGenerator
from src.TextModel import TextModel, HuggingFaceTextModel, MarkovTextModel

_logger = logging.getLogger(__name__)


class FanficHTMLPostCreator(HTMLPostCreator):
    """`HTMLPostCreator` that creates a post with a fanfic generator."""

    _logo_images: ClassVar[List[Path]] = list((Directories.IMAGES_DIR / "fanficlogo").glob("*.png"))

    def __init__(
        self,
        text_generator_class: type[TextGenerator] = FanfictionGenerator,
        tags: Optional[Union[list[str], tuple[str, ...]]] = ("fanfic bot",),
        **kwargs: Any,
    ):
        """Create a `FanficHTMLPostCreator`.

        Parameters
        ----------
        text_generator_class : type[TextGenerator], optional
            `TextGenerator` object to create a post using, by default FanfictionGenerator
        tags : Optional[Union[list[str], tuple[str, ...]]], optional
            list of tags to be used in the post, by default ("fanfic bot",)

        Other Parameters
        ----------------
        **kwargs : dict
            Same as in `HTMLPostCreator`.
        """
        model_map: dict[str, tuple[type[TextModel], str]] = {
            "HuggingFace": (HuggingFaceTextModel, "EleutherAI/gpt-j-6B"),
            "Markov": (MarkovTextModel, "fanfics.bodies"),
        }
        model_probs = {"HuggingFace": 0.9, "Markov": 0.1}
        model_class, model_name = random.choices(list(model_map.values()), weights=list(model_probs.values()), k=1)[0]
        _logger.info(f"Using {model_class.__name__} as the model")
        self.__text_generator = text_generator_class(model_name, model_class)
        try:
            article = self.__text_generator.get_article()
        # If we get an HTTPError from an external service, fall back to local MarkovTextModel
        except HTTPError:
            _logger.error("Received HTTPError from %s, falling back to MarkovTextModel", model_class.__name__)
            model_class, model_name = model_map["Markov"]
            self.__text_generator = text_generator_class(model_name, model_class)
            article = self.__text_generator.get_article()
        header_path = random.choice(self.__class__._logo_images) if len(self.__class__._logo_images) > 0 else None
        super().__init__(
            content=article["body"],
            title=article["title"],
            header_path=header_path,
            use_markdown=True,
            tags=tags,
            **kwargs,
        )