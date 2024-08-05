from decimal import Decimal
from datetime import datetime
from utils.connection import Connection
from utils.hledger import Hledger
from utils.utils import filter_dates, date_range


def preprocess_group_credits_debits(
        postings: list[dict[str, str]]
        ) -> dict[str, dict[tuple[str, str], tuple[Decimal, Decimal]]]:
    """
    Group postings by date and work out the total debit / credit for
    each account.

    Postings are applied to an account and all of its superaccounts.
    """
    # postings = [
    #   {
    #     'field_name': 'value',
    #     ...
    #   }
    # ]

    # credits_debits_by_date = {
    #   date: {
    #     (account, currency): (credit, debit)
    #   }
    # }
    credits_debits_by_date = {}

    for posting in postings:
        currency = posting["commodity"]
        credit = Decimal(posting["credit"] or "0")
        debit = Decimal(posting["debit"] or "0")

        credits_debits = credits_debits_by_date.get(posting["date"], {})
        account = None

        for segment in posting["account"].split(":"):
            if account is None:
                account = segment
            else:
                account = f"{account}:{segment}"

            k = (account, currency)
            old = credits_debits.get(k, (0, 0))
            credits_debits[k] = (old[0] + credit, old[1] + debit)

        credits_debits_by_date[posting["date"]] = credits_debits

    return credits_debits_by_date


def calculate_deltas(
        credits_debits: dict[str, dict[tuple[str, str], tuple[Decimal, Decimal]]]
        ) -> dict[str, dict[tuple[str, str], Decimal]]:
    """ Calculate deltas for all accounts. """
    # credits_debits = {
    #   date: {
    #     (account, currency): (credit, debit)
    #   }
    # }

    # deltas_by_timestamp = {
    #   date: {
    #     (account, currency): delta
    #   }
    # }
    deltas_by_timestamp = {}

    for timestamp, kcds in credits_debits.items():
        deltas_by_timestamp[timestamp] = {
            key: cd[1] - cd[0] for key, cd in kcds.items()
        }

    return deltas_by_timestamp


def get_credit_debits(
        hledger: Hledger,
        file: str = None,
        date: str = None
        ) -> dict[str, dict[tuple[str, str], tuple[Decimal, Decimal]]]:
    postings = hledger.raw_postings(file=file, date=date)

    return preprocess_group_credits_debits(postings)


def run_process(
        hledger: Hledger,
        file: str = None,
        date: str = None) -> None:
    credits_debits = get_credit_debits(hledger, file, date)
    all_deltas = calculate_deltas(credits_debits)

    with Connection() as connection:
        connection.add_daily_deltas(date, all_deltas)


if __name__ == '__main__':
    run_process(Hledger())
