from textwrap import dedent
import unittest

from src.Util import HTMLUtil


class TestHTMLUtil(unittest.TestCase):
    def test_fill_jinja_template(self) -> None:
        """Test filling a Jinja template."""
        filepath = "tests/resources/example.j2"
        expected = "My favorite character is Sonic."
        actual = HTMLUtil.fill_jinja_template(filepath, name="Sonic")
        self.assertEqual(actual, expected)

    def test_html_to_plaintext(self) -> None:
        """Test converting HTML to plain text."""
        html_str = dedent(
            """
                <html>
                    <body>
                        <h1>Hello World!</h1>
                        <p><a href="http://www.example.com">Here</a> is a link.</p>
                        <hr>
                        <ol><li>Item 1</li><li>Item 2</li></ol>
                    </body>
                </html>
            """
        ).strip()
        expected = dedent(
            """
                Hello World!

                Here is a link.

                -----

                  1. Item 1
                  2. Item 2
            """
        ).strip()
        actual = HTMLUtil.html_to_plaintext(html_str)
        self.assertEqual(actual, expected)

    def test_md_to_plaintext(self) -> None:
        """Test converting Markdown to plain text."""
        md_str = dedent(
            """
                # Hello World!

                [Here](http://www.example.com) is a link.

                * * *

                1. Item 1
                2. Item 2

                \\_backslash text\\_ \\\\ _this is emphasized_ \\\\
            """
        ).strip()
        expected = dedent(
            """
                Hello World!

                Here is a link.

                -----

                  1. Item 1
                  2. Item 2

                _backslash text_ \\ this is emphasized \\
            """
        ).strip()
        actual = HTMLUtil.md_to_plaintext(md_str)
        self.assertEqual(actual, expected)
