import copy
import csv
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from utils.connection import Connection
from utils.hledger import Hledger
from utils.utils import date_range

DATE_FAR_FUTURE = '9999-12-31'
MAIN_CURRENCIES_CSV = 'postgres/csv/main_commodities.csv'


def split_price(price: str) -> tuple[str, str, str, str]:
    # [timestamp, currency, rate, target_currency]
    fields = [p for p in re.split("( |\\\".*?\\\"|'.*?')", price) if p.strip()]

    try:
        # P 2000-01-01 USD 1,000.00 VND
        Decimal(fields[3].replace(',', ''))

        return (
            fields[1],
            fields[2].replace('"', ''),
            fields[3],
            fields[4].replace('"', '')
        )
    except InvalidOperation:
        # P 2000-01-01 USD VND 1,000.00
        return (
            fields[1],
            fields[2].replace('"', ''),
            fields[4],
            fields[3].replace('"', '')
        )


def extract_from_hledger(
        raw_prices: list[str]
        ) -> dict[str, dict[tuple[str, str], Decimal]]:
    # {
    #   timestamp => {
    #     (currency, target_currency) => rate
    #   }
    # }
    results = {}

    for raw_price in raw_prices:
        timestamp, currency, str_rate, target_currency = split_price(raw_price)
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


def project_rates(
        limit_date: str,
        explicit_rates: dict[str, dict[tuple[str, str], Decimal]]
        ) -> dict[str, dict[tuple[str, str], Decimal]]:
    """
    Project rates forward if there is a gap, till today.
    Remove dates less than `limit_date` (if present)
    """
    # explicit_rates = {
    #   timestamp => {
    #     (currency, target_currency) => rate
    #   }
    # }

    start_date = datetime.strptime(
        min(explicit_rates.keys()),
        '%Y-%m-%d').date()
    end_date = datetime.now().date()
    previous_rates = {}
    projected_rates = {}

    for d in date_range(start_date, end_date):
        date = d.strftime('%Y-%m-%d')
        rates_of_the_day = explicit_rates.get(date)

        if rates_of_the_day is not None:
            for rate in rates_of_the_day:
                previous_rates[rate] = rates_of_the_day[rate]

        if limit_date is None or date >= limit_date:
            projected_rates[date] = copy.deepcopy(previous_rates)

    return projected_rates


def get_main_currencies():
    with open(MAIN_CURRENCIES_CSV, mode='r') as file:
        reader = csv.reader(file)

        # skip header
        next(reader)

        return [row[0] for row in reader]


def generate_implicit_rates(
        all_explicit_rates: dict[str, dict[tuple[str, str], Decimal]]
        ) -> dict[str, dict[tuple[str, str], Decimal]]:
    # explicit_rates = {
    #   timestamp => {
    #     (currency, target_currency) => rate
    #   }
    # }
    rates = {}
    main_currencies = get_main_currencies()

    for day in sorted(all_explicit_rates.keys()):
        explicit_rates = all_explicit_rates.get(day)
        all_rates_day = {}

        for explicit in explicit_rates:
            source_currency = explicit[0]
            middle_currency = explicit[1]
            middle_rate = explicit_rates.get(explicit)

            all_rates_day[explicit] = middle_rate

            for other_rates_in_the_day in explicit_rates:
                other_middle_currency = other_rates_in_the_day[0]
                target_currency = other_rates_in_the_day[1]
                the_key = (source_currency, target_currency)

                same_currency = source_currency == target_currency
                not_related = middle_currency != other_middle_currency
                can_ignore = (
                    source_currency not in main_currencies and
                    target_currency not in main_currencies
                )
                already_known = the_key in all_rates_day

                if same_currency or not_related or can_ignore or already_known:
                    continue

                other_rate = explicit_rates.get(other_rates_in_the_day)
                new_rate = middle_rate * other_rate
                all_rates_day[the_key] = new_rate

        rates[day] = all_rates_day

    return rates


def calculate_fx_rates(
        date: str,
        raw_prices: list[str]
        ) -> dict[str, dict[tuple[str, str], Decimal]]:
    explicit_rates = extract_from_hledger(raw_prices)
    projected_rates = project_rates(date, explicit_rates)
    rates = generate_implicit_rates(projected_rates)

    return rates


def run_process(
        hledger: Hledger,
        date: str = None) -> None:
    raw_prices = hledger.prices()
    rates = calculate_fx_rates(date, raw_prices)

    with Connection() as connection:
        connection.add_fx_rates(date, rates)


if __name__ == '__main__':
    run_process(Hledger())
