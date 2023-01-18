import ephem
from typing import Optional

from .GeoUtil import get_latlong


def get_day_state(ip: Optional[str] = None) -> str:
    """Return the current state of day or night based on IP.

    Parameters
    ----------
    ip : Optional[str], optional
        IP address to get location of, or current IP if None; by default None

    Returns
    -------
    str
        "day" if it is daytime, otherwise "night"
    """
    lat, lon = get_latlong(ip)
    observer = ephem.Observer()
    observer.lat = lat
    observer.lon = lon

    next_sunrise = observer.next_rising(ephem.Sun()).datetime()
    next_sunset = observer.next_setting(ephem.Sun()).datetime()

    # Daytime => sunset is sooner
    return "day" if next_sunset < next_sunrise else "night"
