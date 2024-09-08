from base64 import b64decode
from io import BytesIO
import numpy as np
from PIL import Image
import unittest
from unittest.mock import patch

from src.Util import ImageUtil


def assert_image_equal(actual: Image.Image, expected: Image.Image) -> None:
    """Assert that two images are equal."""
    np.testing.assert_array_equal(
        np.asarray(actual.convert("RGBA")),
        np.asarray(expected.convert("RGBA")),
    )


class TestImageUtil(unittest.TestCase):
    def test_get_random_color_from_image(self) -> None:
        """Test getting a random color from an image."""
        with patch("random.randrange", return_value=8):
            img = Image.open("tests/resources/square.png")
            expected = (255, 255, 255)
            actual = ImageUtil.get_random_color_from_image(img)
            self.assertEqual(actual, expected)

    def test_tile_image_to_size(self) -> None:
        """Test tiling an image to a given size."""
        img = Image.open("tests/resources/square.png")
        expected = Image.open("tests/resources/square_tiled.png")
        actual = ImageUtil.tile_image_to_size(img, (32, 32))
        assert_image_equal(actual, expected)

    def test_floodfill_color(self) -> None:
        """Test floodfilling an image with a color."""
        img = Image.open("tests/resources/square.png")
        expected = Image.open("tests/resources/square_fill_color_normal.png")
        actual = ImageUtil.floodfill(img, xy=(8, 8), fill=(255, 0, 0), threshold=128)
        assert_image_equal(actual, expected)

    def test_floodfill_pattern(self) -> None:
        """Test floodfilling an image with a pattern."""
        img = Image.open("tests/resources/square.png")
        pattern = Image.open("tests/resources/pattern.png")
        expected = Image.open("tests/resources/square_fill_pattern_normal.png")
        actual = ImageUtil.floodfill(img, xy=(8, 8), fill=pattern, threshold=128)
        assert_image_equal(actual, expected)

    def test_multiply_floodfill(self) -> None:
        """Test floodfilling an image with a color with a multiply blending mode."""
        img = Image.open("tests/resources/square.png")
        expected = Image.open("tests/resources/square_fill_color_multiply.png")
        actual = ImageUtil.multiply_floodfill(img, xy=(8, 8), fill=(255, 0, 0), threshold=128)
        assert_image_equal(actual, expected)

    def test_image_to_data_url(self) -> None:
        """Test creating a data URL from an image."""
        img = Image.open("tests/resources/square.png")
        data_url = ImageUtil.image_to_data_url(img)
        expected_prefix = "data:image/png;base64,"
        self.assertTrue(data_url.startswith(expected_prefix))
        data_url_bytes = b64decode(data_url.removeprefix(expected_prefix))
        data_url_img = Image.open(BytesIO(data_url_bytes))
        assert_image_equal(img, data_url_img)
