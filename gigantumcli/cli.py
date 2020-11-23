import argparse
from gigantumcli.actions import install, update, start, stop, feedback, list_servers, add_server, ExitCLI
import sys


def main():
    # Setup supported components and commands
    actions = {"install": "Install the Gigantum Client Docker Image",
               "update": "Update the Gigantum Client Docker Image",
               "start": "Start the Client",
               "stop": "Stop the Client",
               "add-server": "Add a new Team or Enterprise server to this Client installation",
               "list-servers": "List the available servers for this Client installation",
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
        elif args.action == "add-server":
            add_server(working_dir=args.working_dir)
        elif args.action == "list-servers":
            list_servers(working_dir=args.working_dir)
        else:
            raise ValueError("Unsupported action `{}` provided. Available actions: {}".format(args.action,
                                                                                              ", ".join(actions.keys())))
    except ExitCLI as err:
        print(err)
        sys.exit(1)


if __name__ == '__main__':
    main()
