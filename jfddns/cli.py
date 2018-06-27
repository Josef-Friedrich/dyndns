"""Command line interface for the command jfddns-debug"""

from jfddns._version import get_versions
from jfddns.webapp import app
import argparse
import os


def get_argparser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-v', '--version',
        action='version',
        version=get_versions()['version'],
    )

    parser.add_argument(
        '-c', '--config-file',
    )

    subcommand = parser.add_subparsers(
        dest='subcommand',
        help='Subcommand',
    )
    subcommand.required = True

    serve_parser = subcommand.add_parser('serve')

    serve_parser.add_argument(
        '-p', '--port',
        type=int,
        default=54321,
    )

    return parser


def main():
    args = get_argparser().parse_args()

    if args.config_file:
        os.environ['JFDDNS_CONFIG_FILE'] = args.config_file

    if args.subcommand == 'serve':
        app.run(debug=True, port=args.port)


if __name__ == "__main__":
    app.run(debug=True)
