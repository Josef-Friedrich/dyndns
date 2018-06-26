"""Command line interface for the command jfddns-debug"""

import argparse
from jfddns.webapp import app
from jfddns._version import get_versions


def get_argparser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-p', '--port',
        type=int,
        default=54321,
    )

    parser.add_argument(
        '-v', '--version',
        action='version',
        version=get_versions()['version'],
    )

    parser.add_argument(
        '-c', '--config-file',
    )

    return parser


def debug():
    args = get_argparser().parse_args()
    if hasattr(args, 'config_file'):
        global config_file
        config_file = args.config_file
    app.run(debug=True, port=args.port)


if __name__ == "__main__":
    app.run(debug=True)
