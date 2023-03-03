from typing import List, Optional
import sys
import argparse

from costcoparser.api import get_receipt_json, parse_receipt, write_to_csv


def main(sys_args: Optional[List[str]] = None) -> int:
    if not sys_args:
        sys_args = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog='costcoparser',
        description='Parse Costco JSON reciept data into a CSV.')

    parser.add_argument('-r',
                        '--receipt',
                        required=True,
                        action='append',
                        help='the path to the receipt JSON file')

    args = parser.parse_args(sys_args)

    if not args.receipt:
        parser.print_help()
        sys.exit(1)

    receipt_json = get_receipt_json(args.receipt[0])
    (receipt, metadata) = parse_receipt(receipt_json)
    write_to_csv(receipt, metadata)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
