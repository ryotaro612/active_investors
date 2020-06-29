import sys
import csv
import collections as coll
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
    parser.add_argument("output")
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


def find_active_investors(disruptors, investments):
    """
    Parameters
    ----------
    disruptors: dict
        '<UUID>':
    """
    funding_round_uuids = [
        funding_round["uuid"]
        for disruptor_uuid, disruptor in disruptors.items()
        for funding_round in disruptor["funding_rounds"]
    ]

    active_investors = dict(
        (investment["investor_uuid"], investment["investor_name"])
        for investment in investments
        if investment["funding_round_uuid"] in funding_round_uuids
        and investment["investor_type"] == "organization"
    )
    return active_investors


def find_investor_funding_round_uuids(active_investors, investments):
    """
    """
    return dict(
        (
            uuid,
            {
                "name": name,
                "funding_round_uuids": [
                    investment["funding_round_uuid"]
                    for investment in investments
                    if investment["investor_uuid"] == uuid
                ],
            },
        )
        for uuid, name in active_investors.items()
    )


def find_investor_funding_rounds(investor_funding_round_uuids, funding_rounds):
    """
    """
    funding_round_uuids = set(
        uuid
        for _, investor in investor_funding_round_uuids.items()
        for uuid in investor["funding_round_uuids"]
    )
    active_funding_rounds = dict(
        (funding_round["uuid"], funding_round)
        for funding_round in funding_rounds
        if funding_round["uuid"] in funding_round_uuids
    )
    return dict(
        (
            investor_uuid,
            {
                "name": investor["name"],
                "funding_rounds": [
                    active_funding_rounds[uuid]
                    for uuid in investor["funding_round_uuids"]
                ],
            },
        )
        for investor_uuid, investor in investor_funding_round_uuids.items()
    )


def find_funding_round_types(funding_rounds):
    return list(
        set(
            funding_round["investment_type"]
            for funding_round in funding_rounds
        )
    )


def write_report(investor_funding_rounds, funding_round_types, output):
    """
    """
    with open(output, "w") as stream:
        writer = csv.writer(stream)

        writer.writerow(
            ["active investor uuid", "name"]
            + funding_round_types
            + ["all types"]
        )

        for uuid, investor in investor_funding_rounds.items():
            fundamental = [uuid, investor["name"]]
            funding_rounds = investor["funding_rounds"]
            count = coll.Counter(
                [
                    funding_round["investment_type"]
                    for funding_round in funding_rounds
                ]
            )
            per_type = [
                count.get(funding_round_type, 0)
                for funding_round_type in funding_round_types
            ]
            writer.writerow(fundamental + per_type + [len(funding_rounds)])


if __name__ == "__main__":
    options = parse(sys.argv[1:])
    companies = read_companies(options.company_file)
    funding_rounds = read_csv(options.funding_rounds)
    investments = read_csv(options.investments)
    disruptors = find_funding_rounds(companies, funding_rounds)
    active_investors = find_active_investors(disruptors, investments)
    investor_funding_round_uuids = find_investor_funding_round_uuids(
        active_investors, investments
    )
    investor_funding_rounds = find_investor_funding_rounds(
        investor_funding_round_uuids, funding_rounds
    )
    funding_round_types = find_funding_round_types(funding_rounds)
    write_report(investor_funding_rounds, funding_round_types, options.output)
