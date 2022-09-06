import sys

import src.TextModel.MarkovTriads as MarkovTriads

if __name__ == "__main__":
    MarkovTriads.train(sys.argv[1:])
