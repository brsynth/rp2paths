#!/usr/bin/env python

from rdkit import RDLogger

from rp2paths.RP2paths import build_args_parser, NoScopeMatrix
from brs_utils import (
    create_logger
)


def main():
    parser = build_args_parser()
    args  = parser.parse_args()

    if args.selected_parser is None:
        parser.print_help()
        exit(1)

    # Disable RDKit logging
    RDLogger.DisableLog('rdApp.*')
    # Setup logger
    logger = create_logger('rp2paths', args.loglevel)

    try:
        args.func(args, logger)
    except NoScopeMatrix as e:
        logger.warning(e.message)
        # exit(1)


if __name__ == '__main__':
    main()
