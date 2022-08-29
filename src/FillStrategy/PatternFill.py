import numpy as np

from .FillStrategy import FillStrategy

# TODO: Implement this class and integrate into SonicMaker/Template OCs


class PatternFill(FillStrategy):
    """FillStrategy that fills on a pattern."""

    @property
    def fill_type(self) -> str:
        """Type of the fill, "pattern"."""
        return "pattern"

    @property
    def fill_name(self) -> str:
        """Name of the fill (e.g., "white with black stripes")."""

    def floodfill(self, img: np.ndarray, xy: tuple[int, int], transform_type: str = "noop") -> None:
        """Implements `floodfill` by filling the region with this `PatternFill`.

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
