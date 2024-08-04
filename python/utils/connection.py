from decimal import Decimal
import sqlite3
import os

DUMP_FILE = 'hledger-dump.db'

def adapt_decimal_real(val: Decimal):
    return float(val)


def init_db(conn):
    # tables:
    with open('sqlite/2-tables.sql', 'r') as sql:
        conn.executescript(sql.read())

    # Check about LAG function (used for average calculations)
    # # views:
    # with open('sqlite/3-views.sql', 'r') as sql:
    #     conn.executescript(sql.read())

    # indexes:
    with open('sqlite/5-indexes.sql', 'r') as sql:
        conn.executescript(sql.read())


def create_connection():
    new_db = not os.path.isfile(DUMP_FILE)
    conn = sqlite3.connect(DUMP_FILE)

    if new_db:
        init_db(conn)

    return conn


class Connection:
    def __init__(self):
        self.conn = create_connection()
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.conn.commit()

    def delete_table_from_date(self, table: str, date: str = None) -> None:
        sql = f'delete from {table}'

        if date is not None:
            sql += f" where date >= '{date}'"

        self.cursor.execute(sql)

    def bulk_insert(self, table, fields, params):
        placeholders = "?, " * len(fields)
        placeholders = placeholders[:-2]

        sql = (
            f'insert into {table} '
            f'({", ".join(fields)}) '
            f'values '
            f'({placeholders})')

        self.conn.executemany(sql, params)

    def add_balances(
            self,
            date: str,
            balances: dict[str, dict[tuple[str, str], Decimal]]
            ) -> None:
        # balances = {
        #   timestamp => {
        #     (currency, target_currency) => balance
        #   }
        # }

        table = 'balance_to_date'
        fields = ('date', 'balance', 'account', 'currency')
        params = [
            (timestamp, balance, key[0], key[1])
            for timestamp, records in balances.items()
            for key, balance in records.items()
        ]

        self.delete_table_from_date(table, date)
        self.bulk_insert(table, fields, params)

    def add_daily_deltas(
            self,
            date: str,
            deltas: dict[str, dict[tuple[str, str], Decimal]]
            ) -> None:
        # deltas = {
        #   timestamp => {
        #     (currency, target_currency) => delta
        #   }
        # }

        table = 'daily_delta'
        fields = ('date', 'balance', 'account', 'currency')
        params = [
            (timestamp, delta, key[0], key[1])
            for timestamp, records in deltas.items()
            for key, delta in records.items()
        ]

        self.delete_table_from_date(table, date)
        self.bulk_insert(table, fields, params)

    def add_fx_rates(
            self,
            date: str,
            fx_rates: dict[str, dict[tuple[str, str], Decimal]]
            ) -> None:
        # fx_rates = {
        #   timestamp => {
        #     (currency, target_currency) => rate
        #   }
        # }

        table = 'fx_rate'
        fields = ('date', 'rate', 'currency', 'target_currency')
        params = [
            (timestamp, rate, currencies[0], currencies[1])
            for timestamp, records in fx_rates.items()
            for currencies, rate in records.items()
        ]

        self.delete_table_from_date(table, date)
        self.bulk_insert(table, fields, params)


sqlite3.register_adapter(Decimal, adapt_decimal_real)
