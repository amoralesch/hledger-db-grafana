import subprocess

MAIN_LEDGER = "../ledger/hledger.all.journal"


def hledger_command(args):
    """
    Run a hledger command, throw an error if it fails,
    and return the stdout
    """
    print(f'Running hledger command: {args[0]}')

    ledger_file = MAIN_LEDGER
    real_args = [
        "hledger",
        "-f",
        ledger_file
    ]
    real_args.extend(args)
    proc = subprocess.run(real_args, check=True, capture_output=True)

    return proc.stdout.decode("utf-8")


def hledger_prices() -> list[str]:
    args = ["prices", '--infer-market-prices']

    return hledger_command(args).splitlines()
