import markdown
from PIL import Image
import random
from typing import Any, Optional, Union

from .PostCreator import PostCreator
import src.Directories as Directories
from src.Util.HTMLtoImage import fill_jinja_template, html_to_image
from src.Util.ImageUtil import image_to_data_url


class HTMLPostCreator(PostCreator):
    """`PostCreator` that creates a post having based off an HTML template."""

    def __init__(
        self,
        content: str,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        image: Optional[Image.Image] = None,
        tags: Optional[Union[list[str], tuple[str, ...]]] = None,
        template_name: Optional[str] = None,
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
        title : Optional[str]
            title of the text in the image, by default None
        subtitle : Optional[str]
            subtitle of the text in the image, by default None
        image : Optional[Image.Image]
            image to insert within the image, by default None
        tags : Optional[Union[list[str], tuple[str, ...]]]
            list of tags to be used in the text of the post, by default None
        template_name : Optional[str]
            name of the HTML Jinja template from `images/posttemplate/*.j2` to use, by default None; if None, picks one at random
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
        if template_name:
            self.__template_file = Directories.IMAGES_DIR / "posttemplate" / f"{template_name}.j2"
        else:
            self.__template_file = random.choice(list((Directories.IMAGES_DIR / "posttemplate").glob("*.j2")))
        self.__content = content
        self.__title = title
        self.__subtitle = subtitle
        self.__image = image
        self.__tags = tags
        self.__post_width = width
        self.__post_height = height
        self.__use_markdown = use_markdown
        super().__init__(**kwargs)

    def get_image(self) -> Optional[Image.Image]:
        """Implements `get_image` in `PostCreator` by creating an image, using the post inputs and HTML Jinja template.

        Returns
        -------
        Optional[Image.Image]
            image of the post, or None if long text is preferred
        """
        template_args = {
            "project_dir": str(Directories.PROJECT_DIR),
            "title": self.__title,
            "subtitle": self.__subtitle,
            "content": markdown.markdown(self.__content) if self.__use_markdown else self.__content,
            "image": image_to_data_url(self.__image) if self.__image else None,
        }
        full_html = fill_jinja_template(self.__template_file, **template_args)
        return html_to_image(full_html, width=self.__post_width, height=self.__post_height)

    def get_alt_text(self) -> str:
        """Implements `get_alt_text` in `PostCreator` by using the body text in the post image.

        Returns
        -------
        str
            alt text using the body text in the image
        """
        single_newline = "\n"
        double_newline = "\n\n"
        return f"{(self.__title + double_newline) if self.__title else ''}{self.__content.replace(single_newline, double_newline)}"

    def get_title(self) -> Optional[str]:
        """Implements `get_title` in `PostCreator` by returning the title of the post.

        Returns
        -------
        Optional[str]
            title of the post
        """
        return self.__title

    def get_short_text(self) -> str:
        """Implements `get_short_text` in `PostCreator` by using the title or text, and tags of the post.

        Returns
        -------
        str
            short text of the post
        """
        tags_suffix = " " + " ".join(f"#{tag.replace(' ', '')}" for tag in self.__tags) if self.__tags else ""
        # Use title if there is one, otherwise the text
        content = self.__title or self.__content
        content += tags_suffix
        return content

    def get_long_text(self) -> str:
        """Implements `get_long_text` in `PostCreator` by returning the text of the post.

        Returns
        -------
        str
            long text of the post
        """
        return self.__content.replace("\n", "\n\n")

    def get_tags(self) -> Optional[tuple[str, ...]]:
        """Implements `get_tags` in `PostCreator` by returning the tuple of tags.

        Returns
        -------
        Optional[tuple[str, ...]]
            tags of the post
        """
        return tuple(self.__tags) if self.__tags else None
