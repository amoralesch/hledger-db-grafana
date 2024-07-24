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


def prices() -> list[str]:
    """ Return the list of prices, both implicit and explicit. """
    args = ["prices", '--infer-market-prices']

    return hledger_command(args).splitlines()


def current_commodites():
    """
    Return a list of commodities currently active (i.e. in use today)
    """
    lines = hledger_command(['bal', '-1', '--no-total']).splitlines()
    commodities = []

    for line in lines:
        line = line.strip()
        if '"' not in line:
            # -1,234.56 USD  Assets
            commodities.append(line.split(' ')[1])
        else:
            # -1,234.56 "USD *"  Assets
            start = line.index('"') + 1
            end = line.index('"', start)
            commodities.append(line[start:end])

    return set(commodities)
