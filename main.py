import sys, logging

logging.basicConfig(level=logging.ERROR, format="[ERROR] %(asctime)s: %(message)s")

from args import *
from bot import RedditBot

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.exit(
            '[ERROR!] No options provided. Try using the "-h" flag.'
        )  # args = prompt_args() # Not available in Python 3.10, yet
    else:
        args = cmdline_args()

    if args["verbose"]:
        logging.basicConfig(
            level=logging.INFO, format="[INFO] %(asctime)s: %(message)s"
        )

    if args["creds_file"]:
        try:
            with open(args["creds_file"], "r") as f:
                accounts = f.readlines()
        except FileNotFoundError:
            sys.exit("[ERROR!] Credentials file not found.")
    elif args["username"] and args["password"]:
        accounts = [f"{args['username']}:{args['password']}"]
    else:
        sys.exit("[ERROR!] No credentials provided.")

    if args["links_file"]:
        try:
            with open(args["links_file"], "r") as f:
                links = f.readlines()
        except FileNotFoundError:
            sys.exit("[ERROR!] Links file not found.")
    elif args["url"] and args["action"]:
        links = [(args["url"], args["action"])]
    else:
        sys.exit("[ERROR!] No links provided.")

    bot = RedditBot()

    for acc in accounts:
        if acc not in ["\n", "\r\n"]:
            username, password = acc.split("|")
            bot.login(username, password)

            for entry in links:
                if entry not in ["\n", "\r\n"]:
                    link, action = entry.split("|")
                    bot.vote(bool(int(action)), link)

    bot._dispose()
