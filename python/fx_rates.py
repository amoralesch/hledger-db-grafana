from decimal import Decimal
import subprocess
from utils.connection import Connection

MAIN_LEDGER = "../ledger/hledger.all.journal"


def hledger_command(args):
    """Run a hledger command, throw an error if it fails, and return the
    stdout.
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


def split_price(price: str) -> tuple[str, str, str, str, str]:
    fields = price.replace('"', '').split()

    if len(fields) == 5:
        return fields
    else:
        return (
            fields[0],
            fields[1],
            fields[2] + ' ' + fields[3],
            fields[4],
            fields[5]
        )


def extract_from_hledger_format(raw_prices: list[str]) -> dict[str, dict[tuple[str, str], Decimal]]:
    # {
    #   timestamp => {
    #     (currency, target_currency) => rate
    #   }
    # }
    results = {}

    for raw_price in raw_prices:
        _, timestamp, currency, str_rate, target_currency = split_price(raw_price)
        rate = Decimal(str_rate.replace(',', ''))

        if rate == 0:
            continue

        new_rate = results.get(timestamp, {})
        new_rate[(currency, currency)] = 1
        new_rate[(target_currency, target_currency)] = 1
        new_rate[(currency, target_currency)] = rate
        new_rate[(target_currency, currency)] = 1 / rate

        results[timestamp] = new_rate

    return results


def calculate_fx_rates(raw_prices: list[str]) -> dict[str, dict[tuple[str, str], Decimal]]:
    explicit_rates = extract_from_hledger_format(raw_prices)

    return explicit_rates


def run_process():
    raw_prices = hledger_prices()
    fx_rates = calculate_fx_rates(raw_prices)

    with Connection() as connection:
        connection.add_fx_rates(fx_rates)


if __name__ == '__main__':
    run_process()
