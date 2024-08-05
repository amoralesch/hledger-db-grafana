from decimal import Decimal
from datetime import datetime
from utils.connection import Connection
from utils.hledger import Hledger
from utils.utils import filter_dates, date_range, preprocess_group_credits_debits


def running_totals(
        deltas_by_timestamp: dict[str, dict[tuple[str, str], Decimal]]
        ) -> dict[str, dict[tuple[str, str], Decimal]]:
    """
    Turn `timestamp => key => delta` to `timestamp => key => total` by
    summing deltas in order.
    """
    # deltas_by_timestamp = {
    #   date: {
    #     (account, currency): delta
    #   }
    # }

    current = {}
    out = {}
    start_date = datetime.strptime(
        min(deltas_by_timestamp.keys()),
        '%Y-%m-%d').date()
    end_date = datetime.now().date()

    for d in date_range(start_date, end_date):
        timestamp = d.strftime('%Y-%m-%d')
        today_deltas = deltas_by_timestamp.get(timestamp, {})

        for k, delta in today_deltas.items():
            current[k] = current.get(k, 0) + delta

        out[timestamp] = {k: v for k, v in current.items()}

        # XXX: not sure if this is needed
        # Remove records where balance is 0, only after the second time
        keys_to_remove = [k for k, v in current.items() if v == 0]
        for key in keys_to_remove:
            del current[key]

    return out


def calculate_balances(
        credits_debits: dict[str, dict[tuple[str, str], tuple[Decimal, Decimal]]]
        ) -> dict[str, dict[tuple[str, str], Decimal]]:
    """
    Calculate balance for all accounts.

    Accounts are propagated forward in time: if an account is seen at
    time T, then its balance will also be reported at time T+1, T+2,
    etc.
    """
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

    return running_totals(deltas_by_timestamp)


def get_credit_debits(
        hledger: Hledger,
        depth: int
        ) -> dict[str, dict[tuple[str, str], tuple[Decimal, Decimal]]]:
    postings = hledger.raw_postings()

    return preprocess_group_credits_debits(postings, depth)


def run_process(
        hledger: Hledger,
        date: str = None,
        depth: int = None) -> None:
    credits_debits = get_credit_debits(hledger, depth)
    all_balances = calculate_balances(credits_debits)
    filter_dates(date, all_balances)

    with Connection() as connection:
        connection.add_balances(date, all_balances)


if __name__ == '__main__':
    run_process(Hledger())
