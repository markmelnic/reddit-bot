import sys, logging

from args import *
from args import *
from bot import RedditBot

if __name__ == "__main__":
    # configure logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.ERROR)
    logger.addHandler(logging.StreamHandler())
    logger.addHandler(logging.FileHandler('.log'))
    formatter = logging.Formatter(
        "\033[91m[ERROR!]\033[0m %(asctime)s \033[95m%(message)s\033[0m"
    )
    logger.handlers[0].setFormatter(formatter)

    if len(sys.argv) == 1:
        logger.error("No arguments provided. Use -h or --help for help.")
        sys.exit(1)
    else:
        args = cmdline_args()

    if args["accounts"]:
        try:
            with open(args["accounts"], "r") as f:
                accounts = f.readlines()
        except FileNotFoundError:
            logger.error(f"Accounts file not found: {args['accounts']}")
            sys.exit(1)
    else:
        logger.error("No accounts file provided. Use -h or --help for help.")
        sys.exit(1)

    if args["links"]:
        try:
            with open(args["links"], "r") as f:
                links = f.readlines()
        except FileNotFoundError:
            logger.error(f"Links file not found: {args['links']}")
            sys.exit(1)
    else:
        logger.error("No links file provided. Use -h or --help for help.")
        sys.exit(1)

    bot = RedditBot(
        verbose=args["verbose"]
    )

    for acc in accounts:
        if acc not in ["\n", "\r\n"]:
            username, password = acc.split("|")
            try:
                bot.login(username, password)
            except AssertionError:
                logger.error(f"Invalid account \033[4m{username}\033[0m")
                continue

            for entry in links:
                contents = entry.strip("\n").split("|")
                link = contents[0]
                action = contents[1]
                if action == "upvote":
                    bot.vote(link, True)
                elif action == "downvote":
                    bot.vote(link, False)
                elif action == "comment":
                    bot.comment(link, contents[2])
                elif action in ["join", "leave"]:
                    bot.join_community(link, action == "join")

    bot._dispose()
