#!/bin/bash
set -e

# Confirm python3 is installed
python3 --version

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r ./python/requirements.txt

# all is good, deactivate virtual environment
deactivate
