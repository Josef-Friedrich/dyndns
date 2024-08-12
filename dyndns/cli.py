"""Command line interface for the command dyndns-debug"""

from __future__ import annotations

import argparse

from dyndns import __version__
from dyndns.environment import ConfiguredEnvironment
from dyndns.webapp import create_app


def get_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=__version__,
    )

    parser.add_argument(
        "-c",
        "--config",
    )

    subcommand = parser.add_subparsers(
        dest="subcommand",
        help="Subcommand",
    )
    subcommand.required = True

    serve_parser: argparse.ArgumentParser = subcommand.add_parser("serve")

    serve_parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=54321,
    )

    subcommand.add_parser("check")

    delete_parser = subcommand.add_parser("delete")
    delete_parser.add_argument("fqdn", help="lol")

    subcommand.add_parser("config")

    return parser


def main() -> None:
    args: argparse.Namespace = get_argparser().parse_args()

    env = ConfiguredEnvironment(args.config)

    if args.subcommand == "serve":
        print(f"Running the webapp on port {args.port}")
        create_app(env).run(debug=False, port=args.port)
    elif args.subcommand == "check":
        print("check")
        env.check()
    elif args.subcommand == "config":
        env.print_config()
    elif args.subcommand == "delete":
        print("delete")
    else:
        print(f"Running the webapp on port {args.port}")
        create_app(env).run(debug=False, port=args.port)
