import sys
import csv
import argparse
import logging as lo
import typing as t


def get_logger():
    """
    """
    return lo.getLogger(__name__)


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("company_file")
    parser.add_argument("daily_report_dir")
    return parser


def parse(args: t.List[str]):
    parser = build_parser()
    options = parser.parse_args(args)
    daily_report_dir = (
        options.daily_report_dir[:-1]
        if options.daily_report_dir.endswith("/")
        else options.daily_report_dir
    )
    options.funding_rounds = f"{daily_report_dir}/funding_rounds.csv"
    options.investments = f"{daily_report_dir}/investments.csv"
    return options


def read_companies(company_csv) -> t.Dict[str, str]:
    """

    Examples
    --------
    {'Asana': 'xxxx..xx-yyyy-xxxx'}

    """
    with open(company_csv) as f:
        reader = csv.reader(f)
        return dict((uuid, company_name) for uuid, company_name in reader)


def read_csv(filename):
    with open(filename) as f:
        reader = csv.DictReader(f)
        return [record for record in reader]


def find_funding_rounds(
    companies: t.Dict[str, str], funding_rounds: t.List[t.Dict[str, str]]
):
    """
    """
    return dict(
        (
            company_id,
            {
                "name": name,
                "funding_rounds": [
                    funding_round
                    for funding_round in funding_rounds
                    if funding_round["org_uuid"] == company_id
                ],
            },
        )
        for name, company_id in companies.items()
    )


if __name__ == "__main__":
    options = parse(sys.argv[1:])
    companies = read_companies(options.company_file)
    funding_rounds = read_fundinging_rounds(options.funding_rounds)
    current = find_funding_rounds(companies, funding_rounds)
