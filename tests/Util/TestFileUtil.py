import unittest
from unittest.mock import patch

from src.Util import FileUtil


class TestFileUtil(unittest.TestCase):
    def test_list_load(self) -> None:
        """Test loading a list from a text file, with a fallback if the file doesn't exist."""
        filepath = "tests/resources/text_list.txt"
        expected = ["sonic", "tails", "knuckles", "amy"]
        actual = FileUtil.list_load(filepath)
        self.assertEqual(actual, expected)

    def test_json_load(self) -> None:
        """Test loading json from a file, with a fallback if the file doesn't exist."""
        filepath = "tests/resources/example.json"
        expected = {"test": {"value": 1}}
        actual = FileUtil.json_load(filepath)
        self.assertEqual(actual, expected)

    def test_yaml_load(self) -> None:
        """Test loading yaml from a file, with a fallback if the file doesn't exist."""
        filepath = "tests/resources/example.yml"
        expected = {"test": {"value": 1}}
        actual = FileUtil.yaml_load(filepath)
        self.assertEqual(actual, expected)

    def test_file_to_data_url(self) -> None:
        """Test converting a file to a data url."""
        filepath = "tests/resources/example.yml"
        expected = "data:application/yaml;base64,dGVzdDoKICB2YWx1ZTogMQo="
        # Workaround for guess_type not working properly in github actions
        with patch("mimetypes.guess_type", return_value=("application/yaml", "utf-8")):
            actual = FileUtil.file_to_data_url(filepath)
        self.assertEqual(actual, expected)
