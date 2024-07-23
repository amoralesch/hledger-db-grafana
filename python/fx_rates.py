from decimal import Decimal
import subprocess
import psycopg2
from psycopg2.extras import execute_values
from configparser import ConfigParser

BASE_DIR = './secrets/database.ini'
MAIN_LEDGER = "../ledger/hledger.all.journal"
DB_SCHEMA = 'hledger'


def load_config(filename=BASE_DIR, section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    config = {}

    if parser.has_section(section):
        params = parser.items(section)

        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return config


def connect(config, schema: str):
    """ Connect to the PostgreSQL database server """
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

    def delete_table(self, table: str) -> None:
        sql = f'truncate table {table}'
        self.cursor.execute(sql)

    def bulk_insert(self, table, fields, params):
        sql = (
            f'insert into {table} '
            f'({", ".join(fields)}) '
            f'values '
            f'%s')

        execute_values(self.cursor, sql, params)

    def add_fx_rates(self, fx_rates: dict[str, dict[tuple[str, str], Decimal]]):
        table = 'fx_rate'
        fields = ('date', 'rate', 'currency', 'target_currency')
        params = [
            (timestamp, rate, original_other[0], original_other[1])
            for timestamp, records in fx_rates.items()
            for original_other, rate in records.items()
        ]

        self.delete_table(table)
        self.bulk_insert(table, fields, params)


def hledger_command(args):
    """Run a hledger command, throw an error if it fails, and return the
    stdout.
    """
    print(f'Running hledger command: {args[0]}')

    ledger_file = MAIN_LEDGER
    real_args = [
        "hledger",
        "-f",
        ledger_file
    ]
    real_args.extend(args)
    proc = subprocess.run(real_args, check=True, capture_output=True)

    return proc.stdout.decode("utf-8")


def hledger_prices() -> list[str]:
    args = ["prices", '--infer-market-prices']

    return hledger_command(args).splitlines()


def split_price(price: str) -> tuple[str, str, str, str, str]:
    fields = price.replace('"', '').split()

    if len(fields) == 5:
        return fields
    else:
        return (
            fields[0],
            fields[1],
            fields[2] + ' ' + fields[3],
            fields[4],
            fields[5]
        )


def extract_from_hledger_format(raw_prices: list[str]) -> dict[str, dict[tuple[str, str], Decimal]]:
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


def calculate_fx_rates(raw_prices: list[str]) -> dict[str, dict[tuple[str, str], Decimal]]:
    explicit_rates = extract_from_hledger_format(raw_prices)

    return explicit_rates


def run_process():
    raw_prices = hledger_prices()
    fx_rates = calculate_fx_rates(raw_prices)

    with Connection() as connection:
        connection.add_fx_rates(fx_rates)


if __name__ == '__main__':
    run_process()
