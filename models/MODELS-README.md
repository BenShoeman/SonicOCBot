# Models File Structure

- `../train.py`: Python file to train the models, included within the repo. Use this to train models using the corpora in the `corpus` directory. Run `python3 train.py -h` for help on what to put in here.
- `fanfics.bodies.db`: Markov model SQLite database for text content from all the fanfictions.
- `fanfics.titles.db`: Markov model SQLite database for titles from all the fanfictions.
- `ocdescriptions.{m,f,x}.db`: Markov model SQLite database for text content from OC descriptions, for men/women/nonbinary descriptions respectively.
- `sonicsez.db`: Markov model SQLite database for text content from all Sonic Says segments.
