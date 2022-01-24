import sys
from typing import List

import third_party_clients
from cli import parse_cli, onboarding_failed_report, onboarding_success_report
from model import Employee, StepProcessingError, OnboardingFailedError, Request


# TODO sygnatura tej funkcji ma dużą szansę na rozrost o kolejne argumenty.
# Np timeout, number_of_retries itd.
# Argumenty z warstwy technicznej - api_key mieszają sie z argumentami bizensowymi - employee
def create_jira_account(employee: Employee, api_key):
    try:
        # TODO Klasy klienckie muszą być używane z poziomu modułu, żeby możliwe było ich
        # łatwe patchowanie.
        third_party_clients.JiraClient(api_key).create_account(
            email=employee.email, user_name=f"{employee.name.lower()}.{employee.surname.lower()[0]}"
        )
    except third_party_clients.JiraException as e:
        raise StepProcessingError(f"Creating jira account failed {e}") from e


def create_slack_account(employee: Employee, api_key: str):
    try:
        third_party_clients.SlackClient(api_key).new_account(
            user=f"{employee.name.lower()}.{employee.surname.lower()}",
            email=employee.email,
        )
    except third_party_clients.SlackException as e:
        raise StepProcessingError("Creating slack account failed") from e


def create_gmail_account(employee: Employee, domain: str, api_key: str):
    try:
        email = third_party_clients.GmailClient(api_key).register(
            prefix=f"{employee.name.lower()}.{employee.surname.lower()}",
            domain=domain,
        )
    except third_party_clients.GmailException as e:
        raise StepProcessingError("Creating gmail account failed") from e
    else:
        employee.set_email(email)


def send_invitation_email(employee: Employee, content: str):
    ...


def onboard(employee, args):
    failed_steps = []
    unprocessed_steps = []

    try:
        create_gmail_account(employee, args.domain, args.gmail_api_key)
    except StepProcessingError:
        failed_steps = ["CreateGmailAccount"]
        unprocessed_steps = ["CreateJiraAccount", "CreateSlackAccount"]
        raise OnboardingFailedError(
            failed_steps=failed_steps,
            unprocessed_steps=unprocessed_steps,
            employee=employee
        )
    try:
        create_jira_account(employee, args.jira_api_key)
    except StepProcessingError:
        failed_steps = ["CreateJiraAccount"]
        unprocessed_steps = ["CreateSlackAccount"]
    try:
        create_slack_account(employee, args.slack_api_key)
    except StepProcessingError:
        failed_steps = ["CreateSlackAccount"]

    if failed_steps or unprocessed_steps:
        raise OnboardingFailedError(
            failed_steps=failed_steps,
            unprocessed_steps=unprocessed_steps,
            employee=employee
        )


def main(cli_args: List[str]):
    request: Request = parse_cli(cli_args)
    employee = Employee.new(request.name, request.surname)
    try:
        onboard(employee, request)
    except OnboardingFailedError as e:
        onboarding_failed_report(e)
    else:
        onboarding_success_report(employee)


if __name__ == "__main__":
    main(sys.argv[1:])
