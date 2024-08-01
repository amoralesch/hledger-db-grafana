#!/bin/bash
set -e

ledger_file=''

while getopts 'f:' flag; do
  case "${flag}" in
    f) ledger_file="${OPTARG}" ;;
    *) print_usage
       exit 1 ;;
  esac
done

# Confirm python3 is installed
python3 --version

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r ./python/requirements.txt

python3 ./python/full_import.py -f ${ledger_file}

# all is good, deactivate virtual environment
deactivate
