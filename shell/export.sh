#!/bin/bash
set -e

ledger_file=''
start_date=''

while getopts 'f:b:' flag; do
  case "${flag}" in
    f) ledger_file="${OPTARG}" ;;
    b) start_date="${OPTARG}" ;;
    *) print_usage
       exit 1 ;;
  esac
done

# Confirm python3 is installed
python3 --version

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

python3 ./python/full_import.py -f ${ledger_file} -b ${start_date}

# all is good, deactivate virtual environment
deactivate
