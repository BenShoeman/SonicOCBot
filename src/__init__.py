"""
This package contains all logic for the app, aside from the script `main.py`.

The submodules are as follows:

- **src.App**: Main app logic, makes a post for a random generator type.
- **src.Directories**: Constants for getting directory paths relative to the project root.
- **src.Errors**: Custom errors for the project.
- **src.FillStrategy**: Classes that represent fill strategies, which are used to determine how to floodfill OCs.
- **src.OC**: Classes that represent OCs. This also contains a function to generate an OC. (*At some point, all generators should be under a single base class.*)
- **src.PostCreator**: Classes used to make posts for various social media platforms.
- **src.Poster**: Classes that post onto various social media platforms.
- **src.TextGenerator**: Classes that represent various types of random text generators using TextModel objects (e.g. fanfictions and Sonic says).
- **src.TextModel**: Classes that represent random generation text models.
- **src.UpsertTable**: Represents a SQLite table that can be upserted to; used in `src.TextModel.MarkovTriads`.
- **src.Util**: Various utilities for color and image creation, reading, and manipulating.
"""
