<div align="center">

# Simple bot to interact with Reddit via Selenium with Chromedriver

![PyPI Version](https://img.shields.io/pypi/pyversions/dash.svg)
![License](https://img.shields.io/pypi/l/pyapibp.svg)

</div>

## Usage

First things first, this bot is rather unstable, meaning it has only been tested on Windows, with my internet conection *etc... etc...*. If you encounter any issues, or have any suggestions, feel free to let me know or contribute yourself.

Currently supported interacions:

- login
- upvote
- downvote

Work in progress features:

- reply
- comment
- create post
- join community

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

    -u, --user:
        [str] Account username if only one account is used, otherwise use the "--creds-file" flag.

    -p, --pass:
        [str] Account password if only one account is used, otherwise use the "--creds-file" flag.

    --url:
        [str] Link to interact with if unique, otherwise use the "--links-file" flag.

    --action:
        [int] Only compatible when used together with the "--url" flag, otherwise use the "--links-file" flag. 1 to upvote, 0 to downvote.

    --links-file:
        [path] Read links to interact with from file. The file should be a list of links per line, one per line, following the structure: url|action. Actions can be either 1 to upvote, 0 to downvote. The file should be in the same directory as this script.

    --creds-file:
        [path] Read credentials from file to iterate over multiple accounts. The file should be a list of usernames and passwords, one per line, following the structure: username|password. The file should be in the same directory as this script.

    -v, --verbose:
        [none] Don't print INFO messages to stdout.

#### Examples:

This will upvote the post with the link https://www.reddit.com/r/ProgrammerHumor/comments/s0f0wd/were_not_the_same_bro/ once.

    > py main.py -u testuser -p testpass --url https://www.reddit.com/r/ProgrammerHumor/comments/s0f0wd/were_not_the_same_bro/ --action 1

This will downvote the post with the link https://www.reddit.com/r/ProgrammerHumor/comments/s0f0wd/were_not_the_same_bro/ from 2 accounts.

    > py main.py --creds-file accounts.txt --links-file posts.txt

        where accounts.txt looks like this:
            testuser1|testpass1
            testuser2|testpass2

        and posts.txt looks like this:
            https://www.reddit.com/r/ProgrammerHumor/comments/s0f0wd/were_not_the_same_bro/|0

*A command line GUI is coming as soon as PyInquirer supports Python 3.10 version.*
