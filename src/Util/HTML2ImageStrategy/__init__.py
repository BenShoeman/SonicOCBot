"""
This module defines HTML2ImageStrategy objects, which are used to determine how to create
images from HTML/CSS.

The submodules are as follows:

- **src.Util.HTML2ImageStrategy.HTML2ImageStrategy**: Has the abstract HTML2ImageStrategy class.
- **src.Util.HTML2ImageStrategy.H2IModuleStrategy**:
    HTML2ImageStrategy that uses the `html2image` module. Disabled in favor of PlaywrightStrategy.
- **src.Util.HTML2ImageStrategy.PlaywrightStrategy**: HTML2ImageStrategy that uses Playwright.
"""

from .HTML2ImageStrategy import HTML2ImageStrategy, CSSDict
# from .H2IModuleStrategy import H2IModuleStrategy
from .PlaywrightStrategy import PlaywrightStrategy
