# Set strict mode to ensure errors are caught
Set-StrictMode -Version Latest

$ledgerFile = ''
$startDate = ''
$depthLevel = ''

function Print-Usage {
    Write-Host "Usage: export.ps1 -f <ledger_file> -b <start_date> -d <depth>"
    exit 1
}

param(
    [string]$f,
    [string]$b,
    [string]$d
)

if ($f) { $ledgerFile = $f }
if ($b) { $startDate = $b }
if ($d) { $depthLevel = $d }

# Confirm python3 is installed
python3 --version

# Create a virtual environment
python3 -m venv venv
& "$venvPath\Scripts\Activate.ps1"
pip install -r "./python/requirements.txt"

python3 "./python/full_import.py" -f $ledgerFile -b $startDate -d $depthLevel

# all is good, deactivate virtual environment
deactivate
