"""Command line interface for the command dyndns-debug"""

from __future__ import annotations

import argparse

from dyndns import __version__
from dyndns.webapp import app


def get_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=__version__,
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

    return parser


def main() -> None:
    args: argparse.Namespace = get_argparser().parse_args()
    if args.subcommand == "serve":
        print(f"Running the webapp on port {args.port}")
        app.run(debug=False, port=args.port)
    elif args.subcommand == "check":
        print("check")


if __name__ == "__main__":
    app.run(debug=True)
