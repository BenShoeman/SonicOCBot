# Fonts File Structure

- `*.ttf`: Any `ttf` text files can go in here, which will be used to create the character posts. (Can end in `-Regular.ttf`, which will get ignored when looking for the italic version.)
- `*-Italic.ttf`: Italic forms of the files above. Will fall back to regular version if italic version is not present.

Example files that could go in this directory:

- `Arimo.ttf`
- `Arimo-Italic.ttf`
- `Cousine.ttf`
- `Tinos-Regular.ttf`
- `Tinos-Italic.ttf`

The character posts will be made using three fonts: Arimo, Cousine, and Tinos. Arimo and Tinos will have their italic variants, and Cousine will fall back on the regular version for the italic version.
