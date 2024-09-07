import csv
import io
import subprocess
import re


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
        lines = self.hledger_command(['bal', '-1', '--no-total', '-O', 'json']).splitlines()
        commodities = []

        for line in lines:
            if 'acommodity' not in line:
                continue

            commodities.append(re.findall('"([^"]*)"', line)[1])

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
