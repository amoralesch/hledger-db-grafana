from decimal import Decimal
from utils.connection import Connection
from utils.hledger import Hledger
from utils.utils import preprocess_group_credits_debits


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
        date: str,
        depth: int
        ) -> dict[str, dict[tuple[str, str], tuple[Decimal, Decimal]]]:
    postings = hledger.raw_postings(date=date)

    return preprocess_group_credits_debits(postings, depth)


def run_process(
        hledger: Hledger,
        date: str = None,
        depth: int = None) -> None:
    credits_debits = get_credit_debits(hledger, date, depth)
    all_deltas = calculate_deltas(credits_debits)

    with Connection() as connection:
        connection.add_daily_deltas(date, all_deltas)


if __name__ == '__main__':
    run_process(Hledger())
