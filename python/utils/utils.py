from datetime import timedelta, date
from decimal import Decimal


def date_range(start: date, end: date, step=timedelta(1)):
    """
    Returns all the dates between `start` and `end` inclusive.
    By default, step is one day, but can be changed.
    """
    curr = start

    while curr <= end:
        yield curr
        curr += step


def filter_dates(
        date: str,
        some_list: dict[str, any]
        ) -> None:
    """
    Remove from `some_list` those elements that are _before_ `date`.
    NOTE: it modifies the parameter
    """
    if date is None:
        return

    keys = [a_date for a_date, _ in some_list.items() if a_date < date]

    for x in keys:
        del some_list[x]

def preprocess_group_credits_debits(
        postings: list[dict[str, str]],
        max_depth: int
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
        this_depth = 1

        for segment in posting["account"].split(":"):
            if account is None:
                account = segment
                this_depth = 1
            else:
                account = f"{account}:{segment}"
                this_depth += 1

            if max_depth is not None and this_depth > max_depth:
                break

            k = (account, currency)
            old = credits_debits.get(k, (0, 0))
            credits_debits[k] = (old[0] + credit, old[1] + debit)

        credits_debits_by_date[posting["date"]] = credits_debits

    return credits_debits_by_date
