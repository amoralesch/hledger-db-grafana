#!/bin/bash
set -e

ledger_file=''
start_date=''
depth_level=''

while getopts 'f:b:d:' flag; do
  case "${flag}" in
    f) ledger_file="${OPTARG}" ;;
    b) start_date="${OPTARG}" ;;
    d) depth_level="${OPTARG}" ;;
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

python3 ./python/full_import.py -f ${ledger_file} -b ${start_date} -d ${depth_level}

# all is good, deactivate virtual environment
deactivate
