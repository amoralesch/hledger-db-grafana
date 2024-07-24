from decimal import Decimal
from configparser import ConfigParser
import psycopg2
from psycopg2.extras import execute_values

BASE_DIR = './secrets/'
DB_SCHEMA = 'hledger'


def load_config(
        filename=f'{BASE_DIR}database.ini',
        section='postgresql') -> dict[str, str]:
    """ Reads config info and return a dictionary with the values """
    parser = ConfigParser()
    parser.read(filename)

    if parser.has_section(section):
        params = parser.items(section)

        return { param[0]: param[1] for param in params }
    else:
        raise Exception(
            'Section {0} not found in the {1} file'
            .format(section, filename))


def connect(config, schema: str):
    """ Create a PostgreSQL connection """
    try:
        with psycopg2.connect(
                options=f'-c search_path={schema}',
                **config) as conn:
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)


def create_connection(schema: str):
    return connect(load_config(), schema)


class Connection:
    def __init__(self, schema: str = DB_SCHEMA):
        self.conn = create_connection(schema)
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.conn.commit()

    def delete_table_from_date(self, table: str, date: str = None) -> None:
        if date is None:
            sql = f'truncate table {table}'
        else:
            sql = f"delete from {table} where date >= '{date}'"

        self.cursor.execute(sql)

    def bulk_insert(self, table, fields, params):
        sql = (
            f'insert into {table} '
            f'({", ".join(fields)}) '
            f'values '
            f'%s')

        execute_values(self.cursor, sql, params)

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
