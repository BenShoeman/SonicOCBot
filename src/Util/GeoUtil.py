import logging
import requests
from typing import Optional, Tuple

_logger = logging.getLogger(__name__)


def get_latlong(ip: Optional[str] = None) -> Tuple[str, str]:
    """Get latitude and longitude from ipinfo.io.

    Parameters
    ----------
    ip : Optional[str], optional
        IP address to get location of, or current IP if None; by default None

    Returns
    -------
    Tuple[str, str]
        latitude and longitude
    """
    url = f"https://ipinfo.io/{ip}/json" if ip else "https://ipinfo.io/json"
    response = requests.get(url, timeout=5)
    try:
        response.raise_for_status()
        loc = response.json().get("loc", "0.0,0.0").split(",")
        if len(loc) > 1:
            return loc[0], loc[1]
        else:
            _logger.warning(f"malformed location received from {url}: {loc}; falling back to 0.0, 0.0")
            return "0.0", "0.0"
    except requests.HTTPError as e:
        _logger.warning(f"encountered {e.response.status_code} error from {url}, falling back to 0.0, 0.0")
        return "0.0", "0.0"
    except (requests.ConnectionError, requests.ReadTimeout) as e:
        _logger.warning(f"encountered {type(e).__name__} from {url}, falling back to 0.0, 0.0")
        return "0.0", "0.0"
