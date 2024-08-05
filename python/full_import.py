import balance_to_date
import daily_deltas
import fx_rates
import argparse
from utils.hledger import Hledger

parser = argparse.ArgumentParser()
parser.add_argument(
    '-f',
    '--file',
    nargs='?',
    help='hledger journal',
    required=False)
parser.add_argument(
    '-b',
    '--begin',
    nargs='?',
    help='begin date',
    required=False)
parser.add_argument(
    '-d',
    '--depth',
    nargs='?',
    help='depth level',
    required=False)
args = parser.parse_args()

ledger_file = args.file
start_date = args.begin
depth_level_str = args.depth
depth_level = None

if depth_level_str is not None:
    depth_level = int(depth_level_str)

hledger = Hledger(file=ledger_file)

balance_to_date.run_process(hledger, date=start_date, depth=depth_level)
daily_deltas.run_process(hledger, date=start_date, depth=depth_level)
fx_rates.run_process(hledger, date=start_date)
