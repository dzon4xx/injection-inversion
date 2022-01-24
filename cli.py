import argparse
from typing import List

from model import Request, Employee, OnboardingFailed


def parse_cli(cli_args: List[str]) -> Request:
    parser = argparse.ArgumentParser(description="Onboard new employee")
    parser.add_argument("--name", required=True)
    parser.add_argument("--surname", required=True)
    parser.add_argument("--gmail-api-key", required=True)
    parser.add_argument("--jira-api-key", required=True)
    parser.add_argument("--slack-api-key", required=True)
    parser.add_argument("--domain", required=False, default="stxnext.pl")
    return Request(**vars(parser.parse_args(cli_args)))


def onboarding_failed_report(e: OnboardingFailed):
    name = e.employee.name
    surname = e.employee.surname
    unprocessed_steps = ", ".join([str(step) for step in e.unprocessed_steps])
    failed_steps = ", ".join([str(step) for step in e.failed_steps])
    print(f"Employee onboarding failed. {name=} {surname=} {failed_steps=} {unprocessed_steps=}")


def onboarding_success_report(employee: Employee):
    name = employee.name
    surname = employee.surname
    email = employee.email
    print(f"Employee onboarding successfull. {name=} {surname=} {email=}")
