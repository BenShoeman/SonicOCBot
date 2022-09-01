# Data File Structure

- `animals.yml`: List of animal species with weights to determine which animals are more likely to be used.
- `colors.{general,skintones}.txt`: Provided in repo. List of colors with their RGB triplets, in the following format:
  ```
  ...
  RRR,GGG,BBB:color name
  ...
  ```
- `colors.skintones.gradient.png`: Provided in repo. Gradient of various skin tones to pick from.
- `dictionary.txt`: Provided in repo. Dictionary of words to be used when cleaning corpora.
- `dictionary.propernouns.txt`: Provided in repo. Dictionary of proper nouns (and other capitalized words) to be used when constructing new sentences.
- `names.{m,f,x}.yml`: List of names to pull from with their probabilities of occurring, for men/women/nonbinary names respectively.
- `patterns.yml`: List of regions to apply a pattern on, given a specific species. Each species contains a list of potential patterns in the `images/pattern` directory to use, along with their probabilities of being used. If none of the patterns are used, a plain color is used instead. (See `sonicmaker-fill.yml` below for what a "region" is.) Follows a format similar to below:
  ```yml
  fur:
    cat:
      spots: 0.33
      stripes: 0.33
    dog:
      spots: 0.2
    ...
  outfit:
    ...
  ```
- `personalities.txt`: List of personality traits.
- `schedule-colors.yml`: Provided in repo. YAML file defining background and text colors for image posts starting at the given start times. They don't need to be in order, but the order of the times will be taken into account when figuring the color out.
- `skills.txt`: List of skills.
- `sonicmaker-fill.yml`: YAML file defining positioning of body parts and where to flood fill them. Note that the body parts are placed *in the same order* as they are in the file. Below is the format for this file:
  ```yml
  image-size: [<template-width>, <template-height>]
  part-1:
    optional: <true|false>
    position: [<x-coord of this part>, <y-coord of this part>]
    fill:
      type-1:
        fill-operation:
          region-name-1: [ [<fill x-coord 1>, <fill y-coord 1>], [<fill x-coord 2>, <fill y-coord 2>], ... ]
          region-name-2: [ ... ]
          ...
        another-fill-op:
          ...
        ...
      type-2:
        ...
      ...
  part-2:
    ...
  ...
  ```
  Explanation for each part:
  - `image-size`: Dimensions of the image to generate in pixels.
  - `part-1`: Which body part to place. Images for this should be placed in `/images/sonicmaker/part-1-{type}.png` and should all be the same size.
    Note that these parts will be placed in sequential order; i.e., `part-1` will be placed first, then `part-2`, and so on.
    - `optional`: Whether this part can randomly be omitted or not.
    - `position`: Upper-left corner of where this part should be placed.
    - `fill` contains the actual information on where to fill this part.
      - `type-1` is one of the possible types of this part to choose. This image should be placed in `/images/sonicmaker/part-1-type-1.png`.
        - If you want no fill, leave this field blank (i.e. null).
        - `fill-operation` is what operation you want to do to the color when filling.
          This is to account for colors that should be shaded or brightened in certain areas, for instance.
          Below are the available types of operations:
          - `noop` (for "no-operation")
          - `brighten`
          - `darken`
          - `complementary`
          - `analogous-ccw`
          - `analogous-cw`
        - `region-name-1` under the operation defines the name of the region being filled (e.g., "fur" or "skin").
          Regions stay consistently colored all throughout the OC regardless of the part it is on, and will use a skin tone if set to "skin".
          You can also make it randomly decide between a region name using a pipe character, e.g. "fur|skin".
          The value for this is a list of x,y coordinates indicating the points to flood fill the template at (like flood filling in MS Paint).
- `template-fill.yml`: YAML file defining where to flood fill the templates. Below is the format for this file:
  ```yml
  template-1:
    species: <species-name>
    gender: <gender letter or string>
    fill:
      fill-operation:
        region-name-1: [ [<fill x-coord 1>, <fill y-coord 1>], [<fill x-coord 2>, <fill y-coord 2>], ... ]
        region-name-2: [ ... ]
        ...
      another-fill-op:
        ...
      ...
  template-2:
    ...
  ...
  ```
  Explanation for each part:
  - `template-1`: One of the templates. Images for this should be placed in `/images/template/template-1.png`.
    - `species`: Species of the template, e.g. "hedgehog" or "echidna".
    - `gender`: Gender of the template, either "m", "f", or "x" for man, woman, or nonbinary respectively.
      Can also use a string to indicate a few possible options, e.g. "mf" means man or woman are possible options.
    - `fill` contains the actual information on where to fill this template.
      - `fill-operation` is what operation you want to do to the color when filling. This is identical to the fill operations for Sonic Maker OCs.
