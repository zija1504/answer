import argparse
from argparse import ArgumentParser
import asyncio

from answer.client import runner


def _get_parser() -> ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Stackoverflow answer from your terminal.',
    )

    parser.add_argument(
        'query',
        metavar='QUERY',
        type=str,
        nargs='*',
        help='question to answer',
    )

    parser.add_argument(
        '-c',
        '--color',
        help='enable colorized output',
        action='store_true'
    )
    parser.add_argument(
        '-a',
        '--all',
        help='display full text of answer',
        action='store_true',
    )
    return parser


def main():
    parser = _get_parser()
    args = vars(parser.parse_args())

    if not args['query']:
        parser.print_help()
        return

    results = asyncio.run(runner(args))
    print('\n'.join(results))


if __name__ == "__main__":
    main()
