import sys, logging

logging.basicConfig(level=logging.ERROR, format="[ERROR] %(asctime)s: %(message)s")

from args import *
from bot import RedditBot

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.exit(
            '[ERROR!] No options provided. Try using the "-h" flag.'
        )
    else:
        args = cmdline_args()

    if args["accounts"]:
        try:
            with open(args["accounts"], "r") as f:
                accounts = f.readlines()
        except FileNotFoundError:
            sys.exit("[ERROR!] Credentials file not found.")
    else:
        sys.exit("[ERROR!] No credentials provided.")

    if args["links"]:
        try:
            with open(args["links"], "r") as f:
                links = f.readlines()
        except FileNotFoundError:
            sys.exit("[ERROR!] Links file not found.")
    else:
        sys.exit("[ERROR!] No links provided.")

    bot = RedditBot(
        verbose=args["verbose"]
    )

    for acc in accounts:
        if acc not in ["\n", "\r\n"]:
            username, password = acc.split("|")
            bot.login(username, password)

            for entry in links:
                contents = entry.strip("\n").split("|")
                link = contents[0]
                action = contents[1]
                if action == "upvote":
                    bot.vote(link, True)
                elif action == "downvote":
                    bot.vote(link, False)

    bot._dispose()
