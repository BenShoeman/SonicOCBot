# Models File Structure

- `../train.py`: Python file to train the models, included within the repo. Use this to train models using text files. Run `python3 train.py -h` for help on what to put in here.
- `fanfics.bodies.db.gz`: Markov model SQLite database for text content from all the fanfictions.
- `fanfics.titles.db.gz`: Markov model SQLite database for titles from all the fanfictions.
- `ocdescriptions.{m,f,x}.db.gz`: Markov model SQLite database for text content from OC descriptions, for men/women/nonbinary descriptions respectively.
- `sonicsez.db.gz`: Markov model SQLite database for text content from all Sonic Says segments.
