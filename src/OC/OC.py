from abc import ABC, abstractmethod
import os
from PIL import Image
import random
from typing import Callable, Optional, Union

import src.util.ColorUtil as ColorUtil
import src.Directories as Directories
from src.TextModel.TextModel import TextModel
from src.TextModel.RNNTextModel import RNNTextModel


def _read_standard_list(filepath: Union[str, os.PathLike]) -> list[str]:
    """Read the file into a list separated by new lines, returning an empty list if the file doesn't exist.

    Parameters
    ----------
    filepath : Union[str, os.PathLike]
        file to open

    Returns
    -------
    list[str]
        file contents as a list or empty list if file doesn't exist
    """
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return [line.strip() for line in f.readlines()]
    else:
        print(f"Error reading {filepath}; returning empty list")
        return []


def _read_name_list(filepath: Union[str, os.PathLike]) -> list[tuple[str, float]]:
    """Read the list of names and probabilities.

    The input list will be in the following format:
    ```
    name:probability
    ```

    Parameters
    ----------
    filepath : Union[str, os.PathLike]
        name list to open

    Returns
    -------
    list[tuple[str, float]]
        list of tuples containing names and probabilities of that name's occurrence
    """
    file_list = _read_standard_list(filepath)
    return [((cols := line.split(","))[0], float(cols[1])) for line in file_list]


def _load_rnn_model(model_name: str) -> Optional[TextModel]:
    """Load the RNN model from the model name.

    Parameters
    ----------
    model_name : str
        model name, see `RNNTextModel` for more details

    Returns
    -------
    Optional[TextModel]
        RNN model if applicable, else None
    """
    try:
        model = RNNTextModel(model_name)
    except:
        model = None
    return model


class OC(ABC):
    """Represents an original character with all the information about it.

    Parameters
    ----------
    auto_populate : bool, optional
        whether all fields should be automatically populated, by default True
    """

    _NAMES = {
        gender: _read_name_list(os.path.join(Directories.DATA_DIR, f"names.{gender}.txt"))
        for gender in ("m", "f", "x")
        if os.path.exists(os.path.join(Directories.DATA_DIR, f"names.{gender}.txt"))
    }
    """Contains lists of names and probabilities of those names occurring for various genders."""
    _SPECIES = _read_standard_list(os.path.join(Directories.DATA_DIR, "animals.txt"))
    """List of species."""
    _PERSONALITIES = _read_standard_list(os.path.join(Directories.DATA_DIR, "personalities.txt"))
    """List of personality types."""
    _SKILLS = _read_standard_list(os.path.join(Directories.DATA_DIR, "skills.txt"))
    """List of possible skills."""

    _DESC_MODELS = {gender: _load_rnn_model(f"ocdescriptions.{gender}") for gender in ("m", "f", "x")}

    _TRANSFORM_OPS: dict[str, Callable[[ColorUtil.ColorTuple], ColorUtil.ColorTuple]] = {
        "noop": lambda color: color,
        "darken": ColorUtil.darken_color,
        "brighten": ColorUtil.brighten_color,
        "complementary": ColorUtil.complementary_color,
        "analogous-ccw": ColorUtil.analogous_ccw_color,
        "analogous-cw": ColorUtil.analogous_cw_color,
    }
    """Dict mapping transformation operations to `ColorUtil` functions."""

    def __init__(self, auto_populate: bool = True):
        self._color_regions: dict[str, str] = {}
        # Start as dummy image that will be populated later
        self._image = Image.new("RGB", (1, 1))
        if auto_populate:
            self.populate_info()

    def populate_info(self):
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
        self._generate_description()
        self._generate_image()

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
    def pronouns(self) -> str:
        """Pronouns of the `OC`."""
        if self._gender == "m":
            return "he/him"
        elif self._gender == "f":
            return "she/her"
        else:
            return "they/them"

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
    def color_regions(self) -> dict[str, str]:
        """Dictionary mapping regions of the `OC` to color names.

        For instance, one of these dictionaries might have a key-value pair like below:
        ```
        {
            ...
            "fur": "red",
            ...
        }
        ```
        """
        return self._color_regions.copy()

    # generate_image must define self._image and self._color_regions, where
    # self._image is a Pillow Image and self._color_regions is a dict of region
    # names to color names, e.g. {"fur": "red"}
    @abstractmethod
    def _generate_image(self) -> None:
        """Generate the OC image.

        This must define self._image and self._color_regions, where self._image is an Image
        and self._color_regions is a dict of region names to color names, e.g. {"fur": "red"}.
        See `SonicMakerOC` and `TemplateOC` for more details.
        """
        pass

    def _generate_gender(self) -> None:
        self._gender = " ".join(random.choices(("m", "f", "x"), weights=(49.1, 50.4, 0.5), k=1))

    def _generate_species(self) -> None:
        self._species = random.choice(OC._SPECIES)

    def _generate_age(self) -> None:
        self._age = max(int(round(random.gauss(21, 6))), 13)

    def _generate_name(self) -> None:
        if self._gender == "f":
            self._name = " ".join(random.choices(tuple(item[0] for item in OC._NAMES["f"]), weights=tuple(item[1] for item in OC._NAMES["f"]), k=1))
        elif self._gender == "m":
            self._name = " ".join(random.choices(tuple(item[0] for item in OC._NAMES["m"]), weights=tuple(item[1] for item in OC._NAMES["m"]), k=1))
        else:
            self._name = " ".join(random.choices(tuple(item[0] for item in OC._NAMES["x"]), weights=tuple(item[1] for item in OC._NAMES["x"]), k=1))

    def _generate_personalities(self) -> None:
        self._personalities = random.sample(OC._PERSONALITIES, k=random.randint(1, 3))

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
        n_skills = max(1, round(random.gauss(2, 1.125)))
        self._skills = random.sample(OC._SKILLS, k=n_skills)

    def _generate_description(self) -> None:
        model = OC._DESC_MODELS.get(self.gender)
        if model is not None:
            self._description = model.get_text_block(mean_words=42, stdev_words=20)
        else:
            print(f"Error: ocdescriptions.{self.gender} model could not be loaded.")
            self._description = ""
