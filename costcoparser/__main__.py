from typing import List, Optional, TypedDict
import sys
import argparse
import json
import csv


class Metadata(TypedDict):
    total: int
    subtotal: int
    taxes: int
    date: str
    barcode: str


class Item(TypedDict):
    id: int
    title: str
    price: int


class Receipt(TypedDict):
    items: List[Item]
    metadata: Metadata


def get_receipt_json(receipt):
    try:
        with open(receipt, 'r') as rf:
            return json.load(rf)
    except:
        print('Error: Costco receipt could not be read or was not found.')


def get_item_data(item) -> Item:
    # making the names easier to read (lowercasing)
    item_title = item.get('itemDescription01')
    cleaned_title = item_title[0] + item_title[1:].lower()

    id = item.get('itemNumber')
    title = cleaned_title
    price = item.get('amount')

    return {'id': id, 'title': title, 'price': price}


def get_receipt_metadata(receipts) -> Metadata:
    # we should only end up with one item in this array
    # if we're already filtering receipts by what
    # documentType of WarehouseReceiptDetail.
    receipts = [
        item for item in receipts
        if item['documentType'] == "WarehouseReceiptDetail"
    ]
    receipt = receipts[0]

    total = receipt.get('total')
    subtotal = receipt.get('subTotal')
    taxes = receipt.get('taxes')
    date = receipt.get('transactionDate')
    barcode = receipt.get('transactionBarcode')

    return {
        'total': total,
        'subtotal': subtotal,
        'taxes': taxes,
        'date': date,
        'barcode': barcode
    }


def parse_receipt(receipt) -> Receipt:
    items: List[Item] = []
    receipts = [
        item for item in receipt.get('data').get('receipts') if not None
    ]
    metadata = get_receipt_metadata(receipts)

    for receipt in receipts:
        if receipt['itemArray'] is not None:
            items = [get_item_data(item) for item in receipt['itemArray']]

    return [items, metadata]


def build_metadata_row(row_name, value):
    return {'id': '', 'name': row_name, 'price': value}


def write_to_csv(receipt: Receipt, metadata: Metadata):
    header = ['id', 'name', 'price']
    filename = f"costco-{metadata['date']}.csv"

    tax_row = build_metadata_row('taxes', metadata['taxes'])
    subtotal_row = build_metadata_row('subtotal', metadata['subtotal'])
    total_row = build_metadata_row('total', metadata['total'])

    with open(filename, 'w') as csvfile:
        csvwriter = csv.DictWriter(csvfile, fieldnames=header)
        csvwriter.writeheader()

        for item in receipt:
            csvwriter.writerow({
                'id': item['id'],
                'name': item['title'],
                'price': item['price']
            })

        csvwriter.writerow(tax_row)
        csvwriter.writerow(subtotal_row)
        csvwriter.writerow(total_row)

    print(f'Created {filename}')


def main(sys_args: Optional[List[str]] = None) -> int:
    if not sys_args:
        sys_args = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog='parse-receipt',
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

    receipt = get_receipt_json(args.receipt[0])
    [receipt, metadata] = parse_receipt(receipt)

    write_to_csv(receipt, metadata)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
