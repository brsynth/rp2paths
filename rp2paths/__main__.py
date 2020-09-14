#!/usr/bin/env python

from .RP2paths import build_args_parser, NoScopeMatrix


def _cli():
    parser = build_args_parser()
    args  = parser.parse_args()

    if args.selected_parser is None:
        parser.print_help()
        exit(1)

    try: args.func(args)
    except NoScopeMatrix as e:
        print()
        print(e.message)
        print()
        exit(1)



if __name__ == '__main__':
    _cli()
