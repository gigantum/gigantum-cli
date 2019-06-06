# Copyright (c) 2017 FlashX, LLC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import argparse
from gigantumcli.actions import install, update, start, stop, feedback, ExitCLI
import sys


def main():
    # Setup supported components and commands
    actions = {"install": "Install the Gigantum Client Docker Image",
               "update": "Update the Gigantum Client Docker Image",
               "start": "Start the Client",
               "stop": "Stop the Client",
               "feedback": "Open a web page to provide feedback"
               }

    help_str = ""
    for action in actions:
        help_str = "{}  - {}: {}\n".format(help_str, action, actions[action])

    description_str = "Command Line Interface to use the local Gigantum Client application\n\n"
    description_str = description_str + "The following actions are supported:\n\n{}".format(help_str)

    parser = argparse.ArgumentParser(description=description_str,
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("--tag", "-t",
                        default=None,
                        metavar="<tag>",
                        help="Image Tag to override the 'latest' Docker Image when updating")

    parser.add_argument("--edge", "-e",
                        action='store_true',
                        help="Optional flag indicating if the edge version should be used."
                             " Applicable to install, update, and start commands. You must have access to this image.")

    parser.add_argument("--wait", "-w",
                        metavar="<seconds>",
                        type=int,
                        default=60,
                        help="Number of seconds to wait for Client during `start`")

    parser.add_argument("--yes", "-y",
                        action='store_true',
                        help="Optional flag to automatically accept confirmation prompts")

    parser.add_argument("--working-dir", "-d",
                        metavar="<working directory>",
                        default="~/gigantum",
                        help="Optional parameter to specify a location for the gigantum working directory when starting"
                             "the Client, other than the default (~/gigantum)")

    parser.add_argument("action", help="Action to perform")

    args = parser.parse_args()

    if not args.edge:
        image_name = 'gigantum/labmanager'
    else:
        image_name = 'gigantum/labmanager-edge'

    try:
        if args.action == "install":
            install(image_name)
        elif args.action == "update":
            update(image_name, args.tag, args.yes)
        elif args.action == "start":
            start(image_name, timeout=args.wait, tag=args.tag, working_dir=args.working_dir,
                  accept_confirmation=args.yes)
        elif args.action == "stop":
            stop(args.yes)
        elif args.action == "feedback":
            feedback()
        else:
            raise ValueError("Unsupported action `{}` provided. Available actions: {}".format(args.action,
                                                                                              ", ".join(actions.keys())))
    except ExitCLI as err:
        print(err)
        sys.exit(1)


if __name__ == '__main__':
    main()
