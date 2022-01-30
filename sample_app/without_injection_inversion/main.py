import sys
from typing import List

import third_party_clients
import cli
import model


def onboard(employee: model.Employee, request: model.Request):
    failed_steps = []
    unprocessed_steps = []
    gmail_client = third_party_clients.GmailClient(request.gmail_api_key)
    try:
        email = gmail_client.register(
            prefix=f"{employee.name.lower()}.{employee.surname.lower()}",
            domain=request.domain,
        )
        employee.set_email(email)
    except third_party_clients.GmailException:
        failed_steps = ["CreateGmailAccount"]
        unprocessed_steps = ["CreateJiraAccount", "CreateSlackAccount", "SendInvitationEmail"]
        raise model.OnboardingFailedError(
            failed_steps=failed_steps,
            unprocessed_steps=unprocessed_steps,
            employee=employee,
        )

    try:
        third_party_clients.JiraClient(request.jira_api_key).create_account(
            email=employee.email,
            user_name=f"{employee.name.lower()}.{employee.surname.lower()[0]}",
        )
    except third_party_clients.JiraException:
        failed_steps = ["CreateJiraAccount"]
        unprocessed_steps = ["CreateSlackAccount", "SendInvitationEmail"]

    try:
        third_party_clients.SlackClient(request.slack_api_key).new_account(
            user=f"{employee.name.lower()}.{employee.surname.lower()}",
            email=employee.email,
        )
    except third_party_clients.SlackException:
        failed_steps = ["CreateSlackAccount"]
        unprocessed_steps = ["SendInvitationEmail"]

    try:
        gmail_client.send_email(
            to=employee.email,
            title="Welcome onboard!",
            body=f"We are happy to have you with us {employee.name}",
        )
    except third_party_clients.GmailException as e:
        failed_steps = ["SendInvitationEmail"]

    if failed_steps or unprocessed_steps:
        raise model.OnboardingFailedError(
            failed_steps=failed_steps,
            unprocessed_steps=unprocessed_steps,
            employee=employee,
        )


def main(cli_args: List[str]):
    request: model.Request = cli.parse_cli(cli_args)
    employee = model.Employee.new(request.name, request.surname)
    try:
        onboard(employee, request)
    except model.OnboardingFailedError as e:
        cli.onboarding_failed_report(e)
    else:
        cli.onboarding_success_report(employee)


if __name__ == "__main__":
    main(sys.argv[1:])
