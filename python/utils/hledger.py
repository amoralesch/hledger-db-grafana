import csv
import io
import subprocess
import re
from decimal import Decimal, InvalidOperation


class Hledger():
    def __init__(self, file: str=None):
        self.file = file

    def hledger_command(self, args):
        """
        Run a hledger command, throw an error if it fails,
        and return the stdout
        """
        print(f'Running hledger command: {args[0]}')

        real_args = ["hledger"]

        if self.file is not None:
            real_args.extend(['-f', self.file])

        real_args.extend(args)

        proc = subprocess.run(real_args, check=True, capture_output=True)

        return proc.stdout.decode("utf-8")

    def prices(self) -> list[str]:
        """ Return the list of prices, both implicit and explicit. """
        args = ["prices", '--infer-market-prices']

        return self.hledger_command(args).splitlines()

    def current_commodites(self) -> list[str]:
        """
        Return a list of commodities currently active (i.e. in use today)
        """
        lines = self.hledger_command(['bal', '-1', '--no-total']).splitlines()
        commodities = []

        for line in lines:
            line = line.strip()
            fields = [p for p in re.split("( |\\\".*?\\\"|'.*?')", line) if p.strip()]

            try:
                # -1,234.56 USD  Assets
                Decimal(fields[0].replace(',', ''))

                commodities.append(fields[1].replace('"', ''))
            except InvalidOperation:
                # USD -1,234.56  Assets
                commodities.append(fields[0].replace('"', ''))

        return set(commodities)

    def raw_postings(
            self,
            date: str = None) -> list[dict[str, str]]:
        # [
        #   {
        #     'field_name': 'value',
        #     ...
        #   }
        # ]

        args = ["print", "-O", "csv"]

        if date is not None:
            args.extend(['-b', date])

        return list(csv.DictReader(io.StringIO(self.hledger_command(args))))
