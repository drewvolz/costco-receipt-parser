from typing import List, Optional, Tuple
from typing_extensions import TypedDict
import sys
import json
import csv


class ArrayItem(TypedDict):
    itemDescription01: str
    itemNumber: int
    amount: float


class Item(TypedDict):
    id: Optional[int]
    title: str
    price: Optional[float]


class Metadata(TypedDict, total=False):
    documentType: str
    itemArray: List[ArrayItem]
    total: int
    subTotal: int
    taxes: int
    transactionDate: str


class Receipt(TypedDict):
    items: List[Item]
    metadata: Metadata


class ReceiptList(TypedDict):
    receipts: List[Metadata]


class ReceiptJson(TypedDict):
    data: ReceiptList


def get_receipt_json(file_path: str) -> ReceiptJson:
    loaded_receipt_json: ReceiptJson
    try:
        with open(file_path, 'r') as rf:
            loaded_receipt_json = json.load(rf)
    except Exception:
        print('Error: Costco receipt could not be read or was not found.')

    return loaded_receipt_json


def get_item_data(item: ArrayItem) -> Item:
    # making the names easier to read (lowercasing)
    item_title = item.get('itemDescription01', 'undefined title')
    cleaned_title = item_title[0] + item_title[1:].lower()

    id = item.get('itemNumber')
    title = cleaned_title
    price = item.get('amount')

    parsed_item: Item = {'id': id, 'title': title, 'price': price}
    return parsed_item


def get_receipt_metadata(receipts: List[Metadata]) -> Metadata:
    # we should only end up with one item in this array
    # if we're already filtering receipts by what
    # documentType of WarehouseReceiptDetail.
    receipts = [
        item for item in receipts
        if item['documentType'] == "WarehouseReceiptDetail"
    ]
    receipt = receipts[0]

    total = receipt.get('total', sys.maxsize)
    subtotal = receipt.get('subTotal', sys.maxsize)
    taxes = receipt.get('taxes', sys.maxsize)
    date = receipt.get('transactionDate', 'nodate')

    parsed_metadata: Metadata = {
        'total': total,
        'subTotal': subtotal,
        'taxes': taxes,
        'transactionDate': date,
    }

    return parsed_metadata


def parse_receipt(receipt: ReceiptJson) -> Tuple[List[Item], Metadata]:
    items: List[Item] = []
    receipts = [
        item for item in receipt.get('data', {}).get('receipts', {})
        if not None
    ]
    metadata = get_receipt_metadata(receipts)

    for r in receipts:
        if r['itemArray'] is not None:
            items = [get_item_data(item) for item in r['itemArray']]

    return (items, metadata)


def build_metadata_row(row_name: str, value: int) -> Item:
    return {'id': None, 'title': row_name, 'price': value}


def write_to_csv(receipt: List[Item], metadata: Metadata) -> None:
    header = ['id', 'title', 'price']
    filename = f"costco-{metadata['transactionDate']}.csv"

    tax_row = build_metadata_row('taxes', metadata['taxes'])
    subtotal_row = build_metadata_row('subtotal', metadata['subTotal'])
    total_row = build_metadata_row('total', metadata['total'])

    with open(filename, 'w') as csvfile:
        csvwriter = csv.DictWriter(csvfile, fieldnames=header)
        csvwriter.writeheader()

        for item in receipt:
            csvwriter.writerow({
                'id': item['id'],
                'title': item['title'],
                'price': item['price']
            })

        csvwriter.writerow(tax_row)
        csvwriter.writerow(subtotal_row)
        csvwriter.writerow(total_row)

    print(f'Created {filename}')
