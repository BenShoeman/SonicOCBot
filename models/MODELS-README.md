# Models File Structure

Note that `h5` files are created as part of the training process, but the only thing that is required for the main app to run is the converted `onnx` files and the corresponding `json` files. These Keras models are converted to ONNX models to make deployment much faster due to avoiding downloading the entire Tensorflow library just to run inference.

- `training.ipynb`: Jupyter notebook to train the models, included within the repo. Use this to train models using the corpora in the `corpus` directory.
- `fanfics.bodies.model.{onnx,json}`: Model and index-to-word mapping for text content from all the fanfictions.
- `fanfics.titles.model.{onnx,json}`: Model and index-to-word mapping for titles from all the fanfictions.
- `ocdescriptions.{m,f,x}.model.{onnx,json}`: Model and index-to-word mapping for text content from OC descriptions, for men/women/nonbinary descriptions respectively.
- `sonicsez.model.{onnx,json}`: Model and index-to-word mapping for text content from all Sonic Says segments.
- `punctuation.probabilities.json`: Provided in repo. Probabilities for each part of speech's following punctuation.
- `sentence.sequences.txt`: Provided in repo. Part-of-speech sequences that make up sentences.
