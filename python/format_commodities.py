import re
import argparse
from pathlib import Path


def reformat_prices(text: str, from_c: str, to_c: str):
    pattern = rf'{re.escape(from_c)}(-?\d+(?:,\d{3})*(?:\.\d+)?)'
    replacement = rf'\1 {to_c}'

    reformatted_text = re.sub(pattern, replacement, text)

    return reformatted_text

# Function to read, reformat, and save the file
def process_file(
        file_path: str,
        from_commodity: str,
        to_commodity: str):
    # Read the contents of the file
    with open(file_path, 'r') as file:
        content = file.read()

    # Reformat the prices in the content
    reformatted = reformat_prices(content, from_commodity, to_commodity)
    base_name = Path(file_path).name

    # Write the reformatted content back to the file or to a new file
    with open('reformatted_' + base_name, 'w') as file:
        file.write(reformatted)


parser = argparse.ArgumentParser()
parser.add_argument(
    '-f',
    '--file',
    nargs='?',
    help='hledger journal',
    required=True)
parser.add_argument(
    '-c',
    '--from',
    dest='from_commodity',
    nargs='?',
    help='commodity to search for',
    required=True)
parser.add_argument(
    '-t',
    '--to',
    dest='to_commodity',
    nargs='?',
    help='commodity to replace',
    required=True)
args = parser.parse_args()

file_path = args.file
from_commodity = args.from_commodity
to_commodity = args.to_commodity

process_file(file_path, from_commodity, to_commodity)
base_name = Path(file_path).name
print(f"Prices have been reformatted in 'reformatted_{base_name}'")
