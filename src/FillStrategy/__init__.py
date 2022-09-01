"""
This module defines FillStrategy objects, which are used to determine how to floodfill OCs.

The submodules are as follows:

- **src.FillStrategy.FillStrategy**: Has the abstract FillStrategy class.
- **src.FillStrategy.ColorFill**: FillStrategy that fills on a single color.
- **src.FillStrategy.PatternFill**: FillStrategy that creates and fills on patterns.
"""

import numpy as np

from .FillStrategy import FillStrategy
from .ColorFill import ColorFill
from .PatternFill import PatternFill


_rng = np.random.default_rng()


def create_fill_strategy_for_species(region_type: str, species_type: str, threshold: int = 192) -> FillStrategy:
    """Create a `FillStrategy` object for a given species and region, taking into account pattern probabilities.

    Parameters
    ----------
    region_type : str
        type of region to fill (e.g., "fur" or "skin")
    species_type : str
        type of species (e.g., "tiger")

    Returns
    -------
    FillStrategy
        randomly generated fill strategy for this species and region
    """
    all_probs = PatternFill.PATTERN_PROBABILITIES
    region_fills = all_probs.get(region_type)
    if region_fills:
        species_fills = region_fills.get(species_type)
        if species_fills:
            choices = list(species_fills.keys())
            probs = list(species_fills.values())
            # If sum of probabilities is less than 1, also create a None choice for no fill
            sum_probs = sum(probs)
            if sum_probs < 1:
                choices.append(None)
                probs.append(1 - sum_probs)
            pattern_type = _rng.choice(choices, p=probs)
            if pattern_type:
                return PatternFill(region_type, pattern_type=pattern_type, threshold=threshold)
    # If we couldn't get a PatternFill above, generate a ColorFill and return that
    return ColorFill(region_type, threshold=threshold)
