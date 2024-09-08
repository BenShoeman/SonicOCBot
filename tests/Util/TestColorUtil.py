import numpy as np
import unittest
from unittest.mock import patch

from src.Util import ColorUtil


class TestColorUtil(unittest.TestCase):
    """Tests for the ColorUtil module."""

    def test_to_pil_color_tuple(self) -> None:
        """Test that converting to a color tuple casts all values to ints."""
        self.assertEqual(ColorUtil.to_pil_color_tuple((0, 123.4, 255)), (0, 123, 255))

    def test_hex2rgb(self) -> None:
        """Test converting a hex color to an RGB tuple."""
        hex_value = "#FF0000"
        expected = (255, 0, 0)
        actual = ColorUtil.hex2rgb(hex_value)
        self.assertEqual(actual, expected)

    def test_rgb2hex(self) -> None:
        """Test converting an RGB tuple to a hex string."""
        rgb = (255, 0, 0)
        expected = "#ff0000"
        actual = ColorUtil.rgb2hex(rgb)
        self.assertEqual(actual, expected)

    def test_hsv2hsl(self) -> None:
        """Test converting an HSV image to a HSL image."""
        hsv = np.array([[[0.0, 1.0, 0.5]]], dtype=np.float64)
        expected = np.array([[[0.0, 1.0, 0.25]]], dtype=np.float64)
        actual = ColorUtil.hsv2hsl(hsv)
        np.testing.assert_array_equal(actual, expected)

    def test_hsl2hsv(self) -> None:
        """Test converting an HSL image to a HSV image."""
        hsl = np.array([[[0.0, 1.0, 0.25]]], dtype=np.float64)
        expected = np.array([[[0.0, 1.0, 0.5]]], dtype=np.float64)
        actual = ColorUtil.hsl2hsv(hsl)
        np.testing.assert_array_equal(actual, expected)

    def test_rgb2hsl(self) -> None:
        """Test converting an RGB image to an HSL image."""
        rgb = np.array([[[255, 0, 0]]], dtype=np.uint8)
        expected = np.array([[[0.0, 1.0, 0.5]]], dtype=np.float64)
        actual = ColorUtil.rgb2hsl(rgb)
        np.testing.assert_array_equal(actual, expected)

    def test_hsl2rgb(self) -> None:
        """Test converting an HSL image to an RGB image."""
        hsl = np.array([[[0.0, 1.0, 0.5]]], dtype=np.float64)
        expected = np.array([[[255, 0, 0]]], dtype=np.uint8)
        actual = ColorUtil.hsl2rgb(hsl)
        np.testing.assert_array_equal(actual, expected)

    def test_get_nearest_color_in_colors_list(self) -> None:
        """Test getting the nearest color in a list of colors."""
        colors_list: dict = {"red": (255, 0, 0), "yellow": (255, 255, 0), "blue": (0, 0, 255)}
        color = (246, 197, 8)
        expected = ("yellow", (255, 255, 0))
        actual = ColorUtil.get_nearest_color_in_colors_list(color, colors_list)
        self.assertEqual(actual, expected)

    def test_randomize_color(self) -> None:
        """Test slightly randomizing a color."""
        color = (255, 0, 0)
        with patch("src.Util.ColorUtil._rng") as mock_rng:
            mock_rng.uniform.return_value = 0.01
            mock_rng.normal.return_value = 0.01
            expected = (255, 20, 5)
            actual = ColorUtil.randomize_color(color)
        self.assertEqual(actual, expected)

    def test_brighten(self) -> None:
        """Test that brightening a color increases the lightness."""
        rgb = (128, 128, 128)
        amount = 0.3
        expected = (204, 204, 204)
        actual = ColorUtil.brighten(rgb, amount=amount)
        self.assertEqual(actual, expected)

        rgb_img = np.array([[[128, 128, 128]]], dtype=np.uint8)
        amount = 0.3
        expected_img = np.array([[[204, 204, 204]]], dtype=np.uint8)
        actual_img = ColorUtil.brighten(rgb_img, amount=amount)
        np.testing.assert_array_equal(actual_img, expected_img)

    def test_darken(self) -> None:
        """Test that darkening a color decreases the lightness."""
        rgb = (255, 255, 255)
        amount = 0.3
        expected = (178, 178, 178)
        actual = ColorUtil.darken(rgb, amount=amount)
        self.assertEqual(actual, expected)

        rgb_img = np.array([[[255, 255, 255]]], dtype=np.uint8)
        amount = 0.3
        expected_img = np.array([[[178, 178, 178]]], dtype=np.uint8)
        actual_img = ColorUtil.darken(rgb_img, amount=amount)
        np.testing.assert_array_equal(actual_img, expected_img)

    def test_complementary(self) -> None:
        """Test correctly getting the complementary color."""
        rgb = (0, 255, 0)
        expected = (255, 0, 255)
        actual = ColorUtil.complementary(rgb)
        self.assertEqual(actual, expected)

        rgb_img = np.array([[[0, 255, 0]]], dtype=np.uint8)
        expected_img = np.array([[[255, 0, 255]]], dtype=np.uint8)
        actual_img = ColorUtil.complementary(rgb_img)
        np.testing.assert_array_equal(actual_img, expected_img)

    def test_analogous(self) -> None:
        """Test correctly getting the analogous color."""
        rgb = (0, 255, 0)
        clockwise = False
        expected = (0, 255, 127)
        actual = ColorUtil.analogous(rgb, clockwise=clockwise)
        self.assertEqual(actual, expected)

        rgb = (0, 255, 0)
        clockwise = True
        expected = (127, 255, 0)
        actual = ColorUtil.analogous(rgb, clockwise=clockwise)
        self.assertEqual(actual, expected)

        rgb_img = np.array([[[0, 255, 0]]], dtype=np.uint8)
        clockwise = False
        expected_img = np.array([[[0, 255, 127]]], dtype=np.uint8)
        actual_img = ColorUtil.analogous(rgb_img, clockwise=clockwise)
        np.testing.assert_array_equal(actual_img, expected_img)

        rgb_img = np.array([[[0, 255, 0]]], dtype=np.uint8)
        clockwise = True
        expected_img = np.array([[[127, 255, 0]]], dtype=np.uint8)
        actual_img = ColorUtil.analogous(rgb_img, clockwise=clockwise)
        np.testing.assert_array_equal(actual_img, expected_img)

    def test_contrasting_text_color(self) -> None:
        """Test correctly getting the contrasting text color for the given color."""
        rgb = (10, 10, 10)
        expected = (255, 255, 255)
        actual = ColorUtil.contrasting_text_color(rgb)
        self.assertEqual(actual, expected)

        rgb = (240, 240, 240)
        expected = (0, 0, 0)
        actual = ColorUtil.contrasting_text_color(rgb)
        self.assertEqual(actual, expected)

    def test_get_colors_list(self) -> None:
        """Test correctly getting the list of colors from a file."""
        filename = "tests/resources/color_list.yml"
        expected = {
            "crimson": (220, 20, 60),
            "lime": (50, 205, 50),
            "pink": (255, 192, 203),
            "turquoise": (64, 224, 208),
        }
        actual = ColorUtil.get_colors_list(filename)
        self.assertEqual(actual, expected)
