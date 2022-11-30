<div align="center">

# Simple bot to interact with Reddit via Selenium with Chromedriver

![PyPI Version](https://img.shields.io/pypi/pyversions/dash.svg)
![License](https://img.shields.io/pypi/l/pyapibp.svg)

</div>

## Usage

First things first, this bot is rather unstable, meaning it has only been tested on Windows, with my internet conection *etc... etc...*. If you encounter any issues, or have any suggestions, feel free to let me know or contribute yourself.

Currently supported interacions:

- login
- upvote/downvote post

Work in progress features:

- comment under post
- reply to comment
- create post
- join community
- upvote/downvote last X posts of user/community

## Usage

In the desired folder, clone this repository:

    > git clone https://github.com/markmelnic/Reddit-Bot

Install the dependencies:

    > pip install -r requirements.txt

Download the latest chromedriver here https://chromedriver.chromium.org/downloads and extract `chromedriver.exe` in the same directory as this script.

### Using command line arguments

    > py main.py -h

Available flags:

    -h, --help:
        Show this help message and exit.

    --links:
        [path] File containing liks and actions. The file should be a list of links, one per line, following the structure: url|action. Actions can be either 1 to upvote, 0 to downvote. The file should be in the same directory as this script.

    --accounts:
        [path] File containing credentials for accounts to perform the actions with. The file should be a list of usernames and passwords, one per line, following the structure: username|password. The file should be in the same directory as this script.

    -v, --verbose:
        [none] Print INFO messages to stdout.

#### Examples:

This will downvote the first post and downvote the latter with 2 accounts.

    > py main.py --accounts accounts.txt --links posts.txt

where accounts.txt looks like this:

    testuser1|testpass1
    testuser2|testpass2

and posts.txt looks like this:

    https://www.reddit.com/r/ProgrammerHumor/comments/s0f0wd/were_not_the_same_bro/|1
    https://www.reddit.com/r/ProgrammerHumor/comments/z8ghv8/gotta_save_those_characters/|0
