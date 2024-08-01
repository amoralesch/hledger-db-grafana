import balance_to_date
import daily_deltas
import fx_rates
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    '-f',
    '--file',
    nargs='?',
    help='hledger journal',
    required=False)
args = parser.parse_args()

ledger_file = args.file

balance_to_date.run_process(file=ledger_file)
daily_deltas.run_process(file=ledger_file)
fx_rates.run_process(file=ledger_file)
