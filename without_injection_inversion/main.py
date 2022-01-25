import sys
from typing import List

import third_party_clients
from cli import parse_cli, onboarding_failed_report, onboarding_success_report
from model import Employee, StepProcessingError, OnboardingFailedError, Request


def onboard(employee: Employee, request: Request):
    failed_steps = []
    unprocessed_steps = []

    try:
        email = third_party_clients.GmailClient(request.gmail_api_key).register(
            prefix=f"{employee.name.lower()}.{employee.surname.lower()}",
            domain=request.domain,
        )
        employee.set_email(email)
    except third_party_clients.GmailException:
        failed_steps = ["CreateGmailAccount"]
        unprocessed_steps = ["CreateJiraAccount", "CreateSlackAccount"]
        raise OnboardingFailedError(
            failed_steps=failed_steps,
            unprocessed_steps=unprocessed_steps,
            employee=employee
        )

    try:
        third_party_clients.JiraClient(request.jira_api_key).create_account(
            email=employee.email, user_name=f"{employee.name.lower()}.{employee.surname.lower()[0]}"
        )
    except third_party_clients.JiraException:
        failed_steps = ["CreateJiraAccount"]
        unprocessed_steps = ["CreateSlackAccount"]

    try:
        third_party_clients.SlackClient(request.slack_api_key).new_account(
            user=f"{employee.name.lower()}.{employee.surname.lower()}",
            email=employee.email,
        )
    except third_party_clients.SlackException:
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
