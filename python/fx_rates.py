import copy
import csv
from decimal import Decimal
from datetime import datetime
from utils.connection import Connection
from utils.hledger import Hledger
from utils.utils import date_range

DATE_FAR_FUTURE = '9999-12-31'
MAIN_CURRENCIES_CSV = 'postgres/csv/main_commodities.csv'


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


def project_rates(
        limit_date: str,
        explicit_rates: dict[str, dict[tuple[str, str], Decimal]],
        last_day_currency: dict[str, str]
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
    # ---
    # last_day_currency = { currency: last_date }

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
                date_1 = last_day_currency.get(rate[0], '1900-01-01')
                date_2 = last_day_currency.get(rate[1], '1900-01-01')

                if date <= date_1 and date <= date_2:
                    previous_rates[rate] = rates_of_the_day[rate]

        rates_to_remove = []
        for rate in previous_rates:
            date_1 = last_day_currency.get(rate[0], '1900-01-01')
            date_2 = last_day_currency.get(rate[1], '1900-01-01')

            if date > date_1 or date > date_2:
                rates_to_remove.append(rate)

        for rate in rates_to_remove:
            del previous_rates[rate]

        if limit_date is None or date >= limit_date:
            projected_rates[date] = copy.deepcopy(previous_rates)

    return projected_rates


def calculate_last_day_for_currencies(
        explicit_rates: dict[str, dict[tuple[str, str], Decimal]]
        ) -> dict[str, str]:
    # explicit_rates = {
    #   timestamp => {
    #     (currency, target_currency) => rate
    #   }
    # }
    all_currencies = {}

    for date, kvs in explicit_rates.items():
        for currencies, _ in kvs.items():
            all_currencies[currencies[0]] = date
            all_currencies[currencies[1]] = date

    return all_currencies


def find_last_day_currencies(
        hledger: Hledger,
        explicit_rates: dict[str, dict[tuple[str, str], Decimal]]
        ) -> dict[str, str]:
    # explicit_rates = {
    #   timestamp => {
    #     (currency, target_currency) => rate
    #   }
    # }

    current_commodities = {
        item: DATE_FAR_FUTURE
        for item in hledger.current_commodites()
    }
    return calculate_last_day_for_currencies(explicit_rates) | current_commodities


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
        hledger: Hledger,
        date: str,
        raw_prices: list[str]
        ) -> dict[str, dict[tuple[str, str], Decimal]]:
    explicit_rates = extract_from_hledger(raw_prices)
    last_day_currencies = find_last_day_currencies(hledger, explicit_rates)
    projected_rates = project_rates(date, explicit_rates, last_day_currencies)
    rates = generate_implicit_rates(projected_rates)

    return rates


def run_process(
        hledger: Hledger,
        date: str = None) -> None:
    raw_prices = hledger.prices()
    rates = calculate_fx_rates(hledger, date, raw_prices)

    with Connection() as connection:
        connection.add_fx_rates(date, rates)


if __name__ == '__main__':
    run_process(Hledger())
