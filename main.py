import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a post for the Sonic OC Bot.")
    parser.add_argument(
        "-d",
        "--dummy",
        action="store_true",
        help="don't make a real post, instead print description and show image",
    )
    parser.add_argument(
        "-t",
        "--type",
        type=str,
        choices=["oc", "sonicsez", "fanfic"],
        help="which type of post to make; can be oc, sonicsez, or fanfic",
    )
    parser.add_argument(
        "--sonicmaker",
        action="store_true",
        help="if type is oc, make it a SonicMaker OC",
    )
    parser.add_argument(
        "--templated",
        action="store_true",
        help="if type is oc, make it a template OC",
    )
    args = parser.parse_args()

    import src.App as App

    App.main(
        dummy_post=args.dummy,
        post_type=args.type,
        sonicmaker=args.sonicmaker,
        templated=args.templated,
    )
