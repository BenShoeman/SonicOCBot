# Templates File Structure

This directory contains `.j2` files, stylized HTML Jinja templates that will work for all post types. They use the following fields present in the class [`HTMLPostCreator`](/src/PostCreator/HTMLPostCreator.py):

- `title`
- `subtitle`
- `content`
- `image` (used where URLs accepted, as the image will be converted to a PNG data URL)
- `project_dir` (taken from `Directories.PROJECT_DIR`)
- Color palette fields:
    - `primary_color`
    - `secondary_color`
    - `tertiary_color`
- Determined from their color counterparts, white or black depending on what will be visible:
    - `primary_text`
    - `secondary_text`
    - `tertiary_text`
