import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a post for the Sonic OC Bot.")
    parser.add_argument("--dummy", help="don't make a real post, instead print description and show image", action="store_true")
    args = parser.parse_args()

    import src.App as App
    App.main(dummy_post=args.dummy)
