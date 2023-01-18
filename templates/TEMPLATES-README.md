# Templates File Structure

This directory contains `.j2` files, stylized HTML Jinja templates that will work for all post types. They use the following fields present in the class [`HTMLPostCreator`](/src/PostCreator/HTMLPostCreator.py):

- `project_dir` (taken from `Directories.PROJECT_DIR`)
- `title`
- `subtitle`
- `content`
- Font fields (URL string chosen from random font in [`/fonts`](/fonts/FONTS-README.md)):
    - `regular_font_path`
    - `italic_font_path`
- `night_mode` (True if nighttime at current location or False if daytime)
- Image fields (data URL strings):
    - `image`
    - `overlay`
    - `header`
- Color palette fields:
    - `primary_color`
    - `secondary_color`
    - `tertiary_color`
- Text color fields (determined from their color palette counterparts, white or black for visibility):
    - `primary_text`
    - `secondary_text`
    - `tertiary_text`

The [base template](/templates/base.j2) is provided in the repo, which in addition to the basic structure for all bot image posts, also includes JavaScript to automatically resize text to fit and automatically set the header background color. The [basic template](/templates/basic.j2) is also provided in the repo, which emulates images from the old removed `OCPostCreator` and `TextPostCreator` classes.
