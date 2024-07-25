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

