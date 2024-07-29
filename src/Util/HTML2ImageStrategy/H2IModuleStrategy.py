"""Old method of getting screenshots using the `html2image` module."""

from html2image import Html2Image
import os
from pathlib import Path
from PIL import Image
import tempfile
from typing import Optional, Union

from .HTML2ImageStrategy import HTML2ImageStrategy, CSSDict, dict_to_css


class H2IModuleStrategy(HTML2ImageStrategy):
    """Represents a strategy to convert HTML/CSS to an image using the module `html2image`.

    If `html2image` is not detecting the Chrome/Chromium path, pass it in using the `CHROME_BIN` environment variable.
    """

    def to_image(
        self,
        html_str: str,
        css: Union[str, CSSDict] = "",
        width: int = 1000,
        height: Optional[int] = None,
        crop_transparency: bool = True,
    ) -> Image.Image:
        """Convert HTML to an image using `html2image`.

        If `html2image` is not detecting the Chrome/Chromium path, pass it in using the `CHROME_BIN` environment variable.

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
            whether to crop transparency, by default True

        Returns
        -------
        Image.Image
            HTML and CSS converted to an image
        """
        css_str = dict_to_css(css).strip() if isinstance(css, dict) else css
        # Set height if it's not defined
        height = height if height else width * 5
        with tempfile.NamedTemporaryFile(suffix=".png") as f:
            f_path = Path(f.name)
            h2i = Html2Image(
                browser_executable=os.getenv("CHROME_BIN"),
                output_path=f_path.parent,
                size=(width, height),
                custom_flags=[
                    "--default-background-color=00000000",
                    "--hide-scrollbars",
                    "--disable-gpu",
                    "--force-device-scale-factor=1.00",
                    *os.getenv("CHROME_ARGS", "").split(),
                ],
            )
            h2i.screenshot(html_str=html_str, css_str=css_str, save_as=f_path.name)
            text_img = Image.open(f_path).convert("RGBA")
        if crop_transparency:
            bbox = text_img.getbbox()
            text_img = text_img.crop(bbox)
        return text_img
