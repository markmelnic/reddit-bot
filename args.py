from argparse import ArgumentParser

# from PyInquirer import Token, prompt, style_from_dict


def cmdline_args() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument(
        "-u",
        "--user",
        dest="username",
        help='[str] Account username if only one account is used, otherwise use the "--creds-file" flag.',
    )
    parser.add_argument(
        "-p",
        "--pass",
        dest="password",
        help='[str] Account password if only one account is used, otherwise use the "--creds-file" flag.',
    )
    parser.add_argument(
        "--url",
        dest="url",
        help='[str] Link to interact with if unique, otherwise use the "--links-file" flag.',
    )
    parser.add_argument(
        "--action",
        dest="action",
        help='[int] Only compatible when used together with the "--url" flag, otherwise use the "--links-file" flag. 1 to upvote, 0 to downvote.',
    )
    parser.add_argument(
        "--links-file",
        dest="links_file",
        help="[path] Read links to interact with from file. The file should be a list of links per line, one per line, following the structure: url|action. Actions can be either 1 to upvote, 0 to downvote. The file should be in the same directory as this script.",
    )
    parser.add_argument(
        "--creds-file",
        dest="creds_file",
        help="[path] Read credentials from file to iterate over multiple accounts. The file should be a list of usernames and passwords, one per line, following the structure: username|password. The file should be in the same directory as this script.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        help="[none] Print INFO messages to stdout",
    )

    return vars(parser.parse_args())


# def prompt_args() -> dict:
#     return prompt(
#         style=style_from_dict(
#             {
#                 Token.QuestionMark: "#E91E63 bold",
#                 Token.Selected: "#673AB7 bold",
#                 Token.Instruction: "",
#                 Token.Answer: "#2196F3",
#                 Token.Question: "#FFB333",
#             }
#         )
#     )
