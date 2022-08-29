from abc import ABC, abstractmethod
import numpy as np


class FillStrategy(ABC):
    """Represents a strategy to floodfill an image region."""

    def __init__(self, region_type: str):
        """Create a `FillStrategy` for a specific fill region.

        Parameters
        ----------
        region_type : str
            type of region to fill (e.g., "fur" or "skin")
        """
        self._region_type = region_type

    @property
    def region_type(self) -> str:
        """The type of region this is filling into (e.g., "fur" or "skin")."""
        return self._region_type

    @property
    @abstractmethod
    def fill_type(self) -> str:
        """Type of the fill (e.g. "color" or "pattern")."""

    @property
    @abstractmethod
    def fill_name(self) -> str:
        """Name of the fill (e.g., "red" or "white with black stripes")."""

    @abstractmethod
    def floodfill(self, img: np.ndarray, xy: tuple[int, int], transform_type: str = "noop") -> None:
        """Floodfill an input image array with this `FillStrategy`. Must fill in place.

        Parameters
        ----------
        img : np.ndarray
            image array to floodfill
        xy : tuple[int, int]
            (x,y) coordinate to floodfill
        transform_type : str
            transform operation to apply to this fill, by default "noop";
            can be one of "noop", "darken", "brighten", "complementary", "analogous-ccw", "analogous-cw"
        """
