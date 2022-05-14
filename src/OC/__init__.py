"""
This module defines OC objects, which are used to make OCs.

The submodules are as follows:

- **src.OC.OC**: Has the abstract OC class that represents an original character with all the information about it.
- **src.OC.SonicMakerOC**: Has the OC class that makes OCs based on Sonic Maker template parts.
- **src.OC.TemplateOC**: Has the OC class that makes OCs based on full templates.
"""

import random

from .OC import OC
from .SonicMakerOC import SonicMakerOC
from .TemplateOC import TemplateOC


def generate_oc(pr_original: float = 0.9) -> OC:
    """Generate a new OC and return it.

    Parameters
    ----------
    pr_original : float, optional
        probability that the OC is a more "original" SonicMakerOC vs a TemplateOC, by default 0.9

    Returns
    -------
    OC
        OC object of the new OC, either of type `src.OC.SonicMakerOC.SonicMakerOC` or `src.OC.TemplateOC.TemplateOC`
    """
    if random.random() < pr_original:
        return SonicMakerOC()
    else:
        return TemplateOC()
