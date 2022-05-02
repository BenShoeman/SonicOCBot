import random

from src.OC.OC import OC


def generate_oc(pr_original: float = 0.9) -> OC:
    """Generate a new OC and return it.

    Parameters
    ----------
    pr_original : float, optional
        probability that the OC is a more original Sonic Maker OC, by default 0.9

    Returns
    -------
    OC
        OC object of the new OC
    """
    if random.random() < pr_original:
        from src.OC.SonicMakerOC import SonicMakerOC

        return SonicMakerOC()
    else:
        from src.OC.TemplateOC import TemplateOC

        return TemplateOC()
