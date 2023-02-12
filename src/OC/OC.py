from abc import ABC, abstractmethod
import logging
from PIL import Image
import random
from requests import HTTPError
from typing import Optional

import src.Util.FileUtil as FileUtil
import src.Directories as Directories
from src.FillStrategy import FillStrategy
from src.TextGenerator import TextGenerator, OCBioGenerator
from src.TextModel import TextModel, HuggingFaceTextModel, MarkovTextModel


_logger = logging.getLogger(__name__)


class OC(ABC):
    """Represents an original character with all the information about it."""

    _NAMES = {gender: FileUtil.yaml_load(Directories.DATA_DIR / f"names.{gender}.yml") for gender in ("m", "f", "x")}
    """Contains lists of names and probabilities of those names occurring for various genders."""
    _SPECIES = FileUtil.yaml_load(Directories.DATA_DIR / "animals.yml")
    """List of species."""
    _SPECIES_PARTS = FileUtil.yaml_load(Directories.DATA_DIR / "animal-types.yml")
    """List of parts to use for each species type."""
    _PERSONALITIES = FileUtil.list_load(Directories.DATA_DIR / "personalities.txt")
    """List of personality types."""
    _SKILLS = FileUtil.list_load(Directories.DATA_DIR / "skills.txt")
    """List of possible skills."""

    def __init__(self, desc_generator_class: type[TextGenerator] = OCBioGenerator, auto_populate: bool = True):
        """Create an `OC`.

        Parameters
        ----------
        desc_generator_class : bool, optional
            which text generator class to use to generate the OC description, by default OCBioGenerator
        auto_populate : bool, optional
            whether all fields should be automatically populated, by default True
        """
        self.__text_generator_class = desc_generator_class
        self._fill_regions: dict[str, FillStrategy] = {}
        # Start as dummy image that will be populated later
        self._image = Image.new("RGB", (1, 1))
        if auto_populate:
            self.populate_info()

    def populate_info(self) -> None:
        """Populate all the information about this OC."""
        self._generate_gender()
        self._generate_species()
        self._generate_age()
        self._generate_name()
        self._generate_personalities()
        self._generate_height_weight_units()
        self._generate_height()
        self._generate_weight()
        self._generate_skills()
        self._setup_text_generator()
        self._generate_description()
        self.generate_image()

    @property
    def name(self) -> str:
        """Name of the `OC`."""
        return self._name

    @property
    def species(self) -> str:
        """Species of the `OC`."""
        return self._species

    @property
    def age(self) -> int:
        """Age of the `OC`."""
        return self._age

    @property
    def gender(self) -> str:
        """Gender of the `OC`."""
        return self._gender

    @property
    def gender_full(self) -> str:
        """Gender of the `OC` as a full word."""
        gender_map = {"m": "man", "f": "woman", "x": "nonbinary"}
        return gender_map.get(self._gender, "unknown")

    @property
    def pronouns(self) -> str:
        """Pronouns of the `OC`."""
        gender_map = {"m": "he/him", "f": "she/her", "x": "they/them"}
        return gender_map.get(self._gender, "unknown")

    @property
    def personalities(self) -> list[str]:
        """Personality traits of the `OC`."""
        return self._personalities

    @property
    def height(self) -> str:
        """Height of the `OC` in "X cm" or "Y ft Z in" format, based on metric unit setting."""
        if self._metric_units:
            return f"{self._height} cm"
        else:
            height_in = round(self._height / 2.54)
            feet = height_in // 12
            inches = height_in % 12
            text = f"{feet} ft"
            if inches > 0:
                text += f" {inches} in"
            return text

    @property
    def height_number(self) -> int:
        """Height of the `OC` in cm."""
        return self._height

    @property
    def weight(self) -> str:
        """Weight of the `OC` in "X kg" or "Y lbs" format, based on metric unit setting."""
        if self._metric_units:
            return f"{self._weight} kg"
        else:
            pounds = round(self._weight * 2.20)
            return f"{pounds} lbs"

    @property
    def weight_number(self) -> int:
        """Weight of the `OC` in kg."""
        return self._weight

    @property
    def skills(self) -> tuple[str, ...]:
        """Skills of the `OC` as a tuple of strings."""
        return tuple(self._skills)

    @property
    def description(self) -> str:
        """Description of the `OC`."""
        return self._description

    @property
    def image(self) -> Image.Image:
        """Image of the `OC` as a PIL image."""
        if self._image is not None:
            return self._image.copy()
        return None

    @property
    def fill_regions(self) -> dict[str, str]:
        """Dictionary mapping regions of the `OC` to color descriptions.

        For instance, one of these dictionaries might have a key-value pair like below:
        ```
        {
            ...
            "fur pattern": "white with black stripes",
            "eye color": "red",
            ...
        }
        ```
        """
        return {f"{fill.region_type} {fill.fill_type}": fill.fill_name for fill in self._fill_regions.values()}

    @abstractmethod
    def generate_image(self) -> None:
        """Generate the OC image.

        This must define `self._image` and `self._fill_regions`, where `self._image` is a PIL.Image.Image
        and `self._fill_regions` is a dict of region names to fill strategies.
        See `SonicMakerOC` and `TemplateOC` for more details.
        """

    def _generate_gender(self) -> None:
        self._gender = random.choices(("m", "f", "x"), weights=(48.9, 50.1, 1.0), k=1)[0]

    def _generate_species(self) -> None:
        species = list(OC._SPECIES.keys())
        weights = list(OC._SPECIES[k].get("weight", 1) for k in OC._SPECIES)
        self._species = random.choices(species, weights=weights, k=1)[0]

    def _generate_age(self) -> None:
        self._age = max(int(round(random.gauss(21, 6))), 13)

    def _generate_name(self) -> None:
        names: dict[str, float] = OC._NAMES[self._gender]
        if len(names) > 0:
            self._name: str = random.choices(tuple(names.keys()), weights=tuple(names.values()), k=1)[0]
        else:
            _logger.warn(f"names.{self.gender}.yml could not be loaded or is empty.")

    def _generate_personalities(self) -> None:
        n_personalities = max(1, round(random.gauss(1.75, 0.6)))
        self._personalities = random.sample(OC._PERSONALITIES, k=n_personalities)

    def _generate_height_weight_units(self) -> None:
        self._metric_units = random.choice((True, False))

    def _generate_height(self) -> None:
        # Set result to height value in cm
        self._height = max(65, round(random.gauss(173, 40)))

    def _generate_weight(self) -> None:
        # Set result weight to value in kg, based off the height
        mean_weight = (50.5 + 0.7 * (self._height - 152.0)) if self._height >= 152 else (50.0 + 9.0 * (self._height - 150.0) / 24.0)
        stdev_weight = (2.5 + 2 * ((self._height - 60.0) / 45.0) ** 2) if self._height >= 60.0 else 2.5
        self._weight = max(25, round(random.gauss(mean_weight, stdev_weight)))

    def _generate_skills(self) -> None:
        n_skills = max(1, round(random.gauss(1.75, 1)))
        self._skills = random.sample(OC._SKILLS, k=n_skills)

    def _setup_text_generator(self, model_key: Optional[str] = None) -> None:
        model_map: dict[str, tuple[type[TextModel], str]] = {
            "HuggingFace": (HuggingFaceTextModel, "EleutherAI/gpt-j-6B"),
            "Markov": (MarkovTextModel, "ocdescriptions.{gender}"),
        }
        model_probs = {"HuggingFace": 0.9, "Markov": 0.1}
        if model_key:
            model_class, model_name_base = model_map[model_key]
        else:
            model_class, model_name_base = random.choices(list(model_map.values()), weights=list(model_probs.values()), k=1)[0]
        _logger.info(f"Using {model_class.__name__} as the model")
        model_name = model_name_base.format(gender=self.gender)
        self.__text_generator = self.__text_generator_class(model_name, model_class, oc=self)

    def _generate_description(self) -> None:
        try:
            article = self.__text_generator.get_article()
        # If we get an HTTPError from an external service, fall back to local MarkovTextModel
        except HTTPError:
            _logger.error("Received HTTPError from %s, falling back to MarkovTextModel", self.__text_generator_class.__name__)
            self._setup_text_generator("Markov")
            article = self.__text_generator.get_article()
        self._description = article["body"]
