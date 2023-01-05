import argparse
import logging

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a post for the Sonic OC Bot.")
    parser.add_argument(
        "-l",
        "--log-level",
        type=str,
        default="warn",
        choices=["critical", "error", "warn", "info", "debug", "notset"],
        help="log level to print to console, by default warning",
    )
    parser.add_argument(
        "-d",
        "--dummy",
        type=str,
        choices=["short", "long"],
        help="set log level to info and only log generated description and show image, choosing either short or long post",
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
    parser.add_argument(
        "-U",
        "--data-url",
        action="store_true",
        help="print the post image as a data URL to stdout (only works for dummy posts)",
    )
    args = parser.parse_args()

    log_level = args.log_level.upper()
    if args.dummy and log_level not in ("INFO", "DEBUG", "NOTSET"):
        log_level = "INFO"
    logging.basicConfig(format="[%(asctime)s] {%(name)s} %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S %Z", level=log_level)

    import src.App as App

    App.main(
        dummy_post=args.dummy,
        post_type=args.type,
        sonicmaker=args.sonicmaker,
        templated=args.templated,
        print_data_url=args.data_url,
    )
