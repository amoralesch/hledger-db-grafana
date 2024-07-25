from datetime import timedelta, date


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

