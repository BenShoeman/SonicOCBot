from pathlib import Path
from PIL import Image
import pycmarkgfm as gfm
import random
from typing import Any, ClassVar, Optional, Union

from .PostCreator import PostCreator
import src.Directories as Directories
from src.Util.ColorUtil import ColorTuple, hex2rgb, rgb2hex, contrasting_text_color
from src.Util.FileUtil import yaml_load
from src.Util.HTMLtoImage import fill_jinja_template, html_to_image
from src.Util.ImageUtil import image_to_data_url


class HTMLPostCreator(PostCreator):
    """`PostCreator` that creates a post having based off an HTML template."""

    _PALETTES: ClassVar[dict[str, dict[str, ColorTuple]]] = {
        palette: {typ: hex2rgb(color) for typ, color in colors.items()}
        for palette, colors in yaml_load(Directories.DATA_DIR / "palettes.yml", lambda: {"default": {}}).items()
    }

    def __init__(
        self,
        content: str,
        template_path: Optional[Union[str, Path]] = None,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        image: Optional[Image.Image] = None,
        tags: Optional[Union[list[str], tuple[str, ...]]] = None,
        palette: Optional[dict[str, ColorTuple]] = None,
        width: int = 1200,
        height: int = 680,
        use_markdown: bool = True,
        **kwargs: Any,
    ):
        """Create an `HTMLPostCreator`.

        Parameters
        ----------
        content : str
            body text for the image
        template_path : Optional[Union[str, Path]]
            path of the HTML Jinja template to use, by default None;
            if a directory is provided, picks a random `.j2` file from the directory; if None, uses `Directories.TEMPLATES_DIR`
        title : Optional[str]
            title of the text in the image, by default None
        subtitle : Optional[str]
            subtitle of the text in the image, by default None
        image : Optional[Image.Image]
            image to insert within the image, by default None
        tags : Optional[Union[list[str], tuple[str, ...]]]
            list of tags to be used in the text of the post, by default None
        palette : Optional[dict[str, ColorTuple]]
            palette information for the image, with keys "primary", "secondary", or "tertiary", by default None;
            auto-populated with a palette if None
        width : int, optional
            width of the outputted image, by default 1200
        height : int, optional
            height of the outputted image, by default 680
        use_markdown : bool, optional
            whether to use markdown in `content`, by default True

        Other Parameters
        ----------------
        **kwargs : dict
            Same as in `PostCreator`.
        """
        path = Path(template_path if template_path else Directories.TEMPLATES_DIR)
        if path.is_dir():
            self.__template_file = random.choice(list(path.glob("*.j2")))
        else:
            self.__template_file = path
        self._content = content
        self._title = title
        self._subtitle = subtitle
        self._image = image
        self._tags = tags
        if palette:
            self.__palette = palette
        else:
            self.__palette = random.choice(list(self.__class__._PALETTES.values()))
        self._post_width = width
        self._post_height = height
        self._use_markdown = use_markdown
        super().__init__(**kwargs)

    def get_image(self) -> Optional[Image.Image]:
        """Implements `get_image` in `PostCreator` by creating an image, using the post inputs and HTML Jinja template.

        The fields that will be filled out in the template are the following:
        - `title`
        - `subtitle`
        - `content`
        - `image` (this is the input image converted to a PNG data URL)
        - `project_dir` (taken from `Directories.PROJECT_DIR`)
        - Color palette fields:
            - `primary_color`
            - `secondary_color`
            - `tertiary_color`
        - Determined from their color counterparts, white or black depending on what will be visible:
            - `primary_text`
            - `secondary_text`
            - `tertiary_text`

        Returns
        -------
        Optional[Image.Image]
            image of the post, or None if long text is preferred
        """
        # Return no image if preferring long text and no input image
        if self._prefer_long_text and not self._image:
            return None
        template_args = {
            "project_dir": str(Directories.PROJECT_DIR),
            "title": self._title,
            "subtitle": self._subtitle if not self._prefer_long_text else None,
            "content": (gfm.gfm_to_html(self._content) if self._use_markdown else self._content) if not self._prefer_long_text else "",
            "image": image_to_data_url(self._image) if self._image else None,
            "primary_color": rgb2hex(self.__palette.get("primary", (0, 0, 0))),
            "secondary_color": rgb2hex(self.__palette.get("secondary", (0, 0, 0))),
            "tertiary_color": rgb2hex(self.__palette.get("tertiary", (0, 0, 0))),
            "primary_text": rgb2hex(contrasting_text_color(self.__palette.get("primary", (0, 0, 0)))),
            "secondary_text": rgb2hex(contrasting_text_color(self.__palette.get("secondary", (0, 0, 0)))),
            "tertiary_text": rgb2hex(contrasting_text_color(self.__palette.get("tertiary", (0, 0, 0)))),
        }
        full_html = fill_jinja_template(self.__template_file, **template_args)
        return html_to_image(full_html, width=self._post_width, height=self._post_height)

    def get_alt_text(self) -> Optional[str]:
        """Implements `get_alt_text` in `PostCreator` by using the body text in the post image.

        Returns
        -------
        str
            alt text using the body text in the image
        """
        single_newline = "\n"
        double_newline = "\n\n"
        return f"{(self._title + double_newline) if self._title else ''}{self._content.replace(single_newline, double_newline)}"

    def get_title(self) -> Optional[str]:
        """Implements `get_title` in `PostCreator` by returning the title of the post.

        Returns
        -------
        Optional[str]
            title of the post
        """
        return self._title

    def get_short_text(self) -> str:
        """Implements `get_short_text` in `PostCreator` by using the title or text, and tags of the post.

        Returns
        -------
        str
            short text of the post
        """
        tags_suffix = " " + " ".join(f"#{tag.replace(' ', '')}" for tag in self._tags) if self._tags else ""
        # Use title if there is one, otherwise the text
        content = self._title or self._content
        content += tags_suffix
        return content

    def get_long_text(self) -> str:
        """Implements `get_long_text` in `PostCreator` by returning the text of the post.

        Returns
        -------
        str
            long text of the post
        """
        return self._content.replace("\n", "\n\n")

    def get_tags(self) -> Optional[tuple[str, ...]]:
        """Implements `get_tags` in `PostCreator` by returning the tuple of tags.

        Returns
        -------
        Optional[tuple[str, ...]]
            tags of the post
        """
        return tuple(self._tags) if self._tags else None
