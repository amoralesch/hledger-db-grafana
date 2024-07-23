from decimal import Decimal
from utils.connection import Connection
from utils.hledger import hledger_prices

START_DATE='2024-01-01'


def split_price(price: str) -> tuple[str, str, str, str, str]:
    fields = price.replace('"', '').split()

    if len(fields) == 5:
        # P 2000-01-01 USD 1.00 USD
        return fields
    else:
        # P 2000-01-01 "USD *" 2.00 USD
        return (
            fields[0],
            fields[1],
            fields[2] + ' ' + fields[3],
            fields[4],
            fields[5]
        )


def extract_from_hledger_format(
        raw_prices: list[str]
        ) -> dict[str, dict[tuple[str, str], Decimal]]:
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


def calculate_fx_rates(
        raw_prices: list[str]
        ) -> dict[str, dict[tuple[str, str], Decimal]]:
    explicit_rates = extract_from_hledger_format(raw_prices)

    return explicit_rates


def filter_rates(
        date: str,
        rates: dict[str, dict[tuple[str, str], Decimal]]
        ) -> dict[str, dict[tuple[str, str], Decimal]]:
    if date is None:
        return rates

    keys = [a_date for a_date, _ in rates.items() if a_date < date]
    for x in keys:
        del rates[x]

    return rates


def run_process(date: str = None):
    raw_prices = hledger_prices()
    fx_rates = calculate_fx_rates(raw_prices)
    rates = filter_rates(date, fx_rates)

    with Connection() as connection:
        connection.add_fx_rates(date, rates)


if __name__ == '__main__':
    run_process(START_DATE)
