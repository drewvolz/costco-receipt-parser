# Costco receipt parser

A set of scripts to turn Costco's json receipt into a csv for further processing.

Costco's printed and online receipts truncate item names for brevity. The full data can be found in the graphql response in the same data that builds the receipt you see online. We can create our own receipt with more context and customization by using the fields which have the full names of items and their metadata.

## How to get your receipt json

### Option 1: Javascript (auto fetch + convert)

This method can download and convert a web receipt to CSV using only the javascript console.

1. Sign-in and navigate to https://www.costco.com/OrderStatusCmd
2. Click on the "In-Warehouse" tab
3. Click on the "View Receipt" button
4. Open the Web Inspector
5. Copy/paste the contents of [`downloader.js`](https://github.com/drewvolz/costco-receipt-parser/blob/js-downloader-parser-converter/costcoparser/script/downloader.js) from the `js-downloader-parser-converter` branch into the console

### Option 2: Python (manual fetch + convert)

This method involves manually downloading the receipt's json and then running a python conversion script.

The python script assumes you have gone through the steps below to first get your receipt json.

It cannot fetch this data for you (unlike Option 1).

For Safari:

1. Open the Web Inspector and inspect the network requests
   - Right click > Inspect Element > Network > XHR/Fetch
2. Sign-in and navigate to https://www.costco.com/OrderStatusCmd
3. Click on the "In-Warehouse" tab
4. Click on the "View Receipt" button
5. Click on the "graphql" document in the inspector
6. Copy/paste the response content into a file, e.g. "receipt.json"

---

Requires Python 3.6+.

```shell script
$ python3 -m venv ./venv
$ source ./venv/bin/activate # or activate.csh or activate.fish
$ pip install -r requirements-dev.txt
$ pip install -r requirements.txt
$ python3 -m costcoparser
```

Other commands:

## CLI

```shell script
$ python3 -m costcoparser --help
```

<!--- START USAGE -->
```shell script
usage: costcoparser [-h] -r RECEIPT

Parse Costco JSON reciept data into a CSV.

options:
  -h, --help            show this help message and exit
  -r RECEIPT, --receipt RECEIPT
                        the path to the receipt JSON file
```
<!--- END USAGE -->

The main CLI entry point; see `--help`.

Basic usage is as follows:

```shell script
$ python3 -m costcoparser -r receipt.json
```

## Misc. Scripts

```shell script
$ make
```

An overall wrapper for:
* Type checking and linting invoked with `mypy` via rules that live inside `.mypy.ini`.
* Formatting invoked via `yapf` via rules that live inside `script/format`.
* Updating usage in the README if the help invocation changes via `script/update-usage.py`

```shell script
$ make format
```

Keeping things tidy.

```shell script
$ make lint
```

Keeping things type-checked and linted.

---

You may notice that there are multiple `requirements*.txt` files. They are split apart so that the dependencies install easily.

| filename                  | why                                          |
| ------------------------- | -------------------------------------------- |
| `requirements.txt`        | Common runtime dependencies                  |
| `requirements-dev.txt`    | Development dependencies – mypy, yapf, etc   |
