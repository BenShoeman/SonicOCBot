"""Method of getting screenshots using Playwright."""

from io import BytesIO
import os
from PIL import Image
from playwright.sync_api import sync_playwright, Browser
from typing import Optional, Union

from src.Directories import TEMPLATES_DIR
from .HTML2ImageStrategy import HTML2ImageStrategy, CSSDict, dict_to_css


class PlaywrightStrategy(HTML2ImageStrategy):
    """Represents a strategy to convert HTML/CSS to an image using Playwright."""

    def __init__(self, browser: str = os.getenv("PLAYWRIGHT_BROWSER", "webkit")) -> None:
        """Create a `PlaywrightStrategy` optionally with a choice of browser."""
        self._browser = browser

    def to_image(
        self,
        html_str: str,
        css: Union[str, CSSDict] = "",
        width: int = 1000,
        height: Optional[int] = None,
        crop_transparency: bool = True,
    ) -> Image.Image:
        """Convert HTML to an image using Playwright.

        Make sure to run `playwright install` beforehand to install the browser dependencies.

        Parameters
        ----------
        html_str : str
            HTML string to convert
        css : Union[str, CSSDict], optional
            CSS string to use for styling, or dict containing selectors as keys and attribute subdicts, by default ""
        width : int, optional
            width of the exported image, by default 1000
        height : int, optional
            height of the exported image, by default 5*width (intended to be cropped off later)
        crop_transparency : bool, optional
            whether to crop transparency; irrelevant here

        Returns
        -------
        Image.Image
            HTML and CSS converted to an image
        """
        css_str = dict_to_css(css).strip() if isinstance(css, dict) else css
        # Set height if it's not defined
        height = height if height else width * 5
        with sync_playwright() as pw:
            browser: Browser = getattr(pw, self._browser).launch(headless=True)
            page = browser.new_page()
            viewport_height = height if height else (page.viewport_size["height"] if page.viewport_size else 5 * width)
            page.set_viewport_size({"width": width, "height": viewport_height})
            # Browsers don't like local file paths on about:blank, so load a blank file before overwriting page contents
            page.goto(f"file://{TEMPLATES_DIR}/blank.html")
            page.set_content(html_str)
            if css_str:
                page.add_style_tag(content=css_str)
            img_bytes = page.screenshot(
                full_page=True,
                clip={"x": 0, "y": 0, "width": width, "height": viewport_height} if height else None,
            )
            browser.close()
        img = Image.open(BytesIO(img_bytes)).convert("RGBA")
        return img
