import ephem
import unittest
from unittest.mock import patch

from src.Util import TimeUtil


class TestTimeUtil(unittest.TestCase):
    def test_get_day_state(self) -> None:
        """Test getting the time of day state."""
        with patch("src.Util.TimeUtil.get_latlong") as mock_get_latlong:
            mock_observer = ephem.Observer()
            mock_observer.date = "2024-09-01 19:00:00"
            with patch("ephem.Observer", return_value=mock_observer):
                mock_get_latlong.return_value = ("39.7420", "-104.9915")
                self.assertEqual("day", TimeUtil.get_day_state())
