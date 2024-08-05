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
depth_level = args.depth

hledger = Hledger(file=ledger_file)

balance_to_date.run_process(hledger, date=start_date)
daily_deltas.run_process(hledger, date=start_date)
fx_rates.run_process(hledger, date=start_date)
