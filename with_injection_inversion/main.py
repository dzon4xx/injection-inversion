import sys
from typing import List

from cli import parse_cli, onboarding_failed_report, onboarding_success_report
from model import (
    Request,
    Employee,
    StepProcessingError,
    OnboardingStep,
    OnboardingFailedError,
)
from third_party_clients import (
    JiraClient,
    SlackClient,
    GmailClient,
    JiraException,
    GmailException,
    SlackException,
)


class CreateJiraAccount(OnboardingStep):
    interrupts_flow = False

    def __init__(self, client: JiraClient):
        self._client: JiraClient = client

    def run(self, employee: Employee):
        try:
            self._client.create_account(
                email=employee.email,
                user_name=f"{employee.name.lower()}.{employee.surname.lower()[0]}",
            )
        except JiraException as e:
            raise StepProcessingError(f"Creating jira account failed {e}") from e


class CreateSlackAccount(OnboardingStep):
    interrupts_flow = False

    def __init__(self, client: SlackClient):
        self._client: SlackClient = client

    def run(self, employee: Employee):
        try:
            self._client.new_account(
                user=f"{employee.name.lower()}.{employee.surname.lower()}",
                email=employee.email,
            )
        except SlackException as e:
            raise StepProcessingError("Creating slack account failed") from e


class CreateGmailAccount(OnboardingStep):
    interrupts_flow = True

    def __init__(self, client: GmailClient, domain: str):
        self._client: GmailClient = client
        self._domain = domain

    def run(self, employee: Employee):
        try:
            email = self._client.register(
                prefix=f"{employee.name.lower()}.{employee.surname.lower()}",
                domain=self._domain,
            )
        except GmailException as e:
            raise StepProcessingError("Creating gmail account failed") from e
        else:
            employee.set_email(email)


# class SendInvitationEmail(OnboardingStep):
#     def run(self, employee: Employee):
#         ...


def onboard(employee: Employee, steps: List[OnboardingStep]) -> None:
    """Runs all onboarding steps.

    In case of errors notifies about failed and/or unprocessed steps"""

    failed_steps = []
    unprocessed_steps = []
    for step_num, step in enumerate(steps):
        try:
            step.run(employee)
        except StepProcessingError:
            if step.interrupts_flow:
                failed_steps.append(step)
                unprocessed_steps = steps[step_num + 1 :]
                break
            else:
                failed_steps.append(step)

    if failed_steps or unprocessed_steps:
        raise OnboardingFailedError(
            failed_steps=failed_steps,
            unprocessed_steps=unprocessed_steps,
            employee=employee,
        )

    return None


def main(cli_args: List[str]):
    request: Request = parse_cli(cli_args)
    # Dependency injection in action.
    # Dependencies are created externally and passed to the business function.
    try:
        employee = Employee.new(request.name, request.surname)
        onboard(
            employee=employee,
            steps=[
                CreateGmailAccount(
                    client=GmailClient(request.gmail_api_key), domain=request.domain
                ),
                CreateJiraAccount(client=JiraClient(request.jira_api_key)),
                CreateSlackAccount(client=SlackClient(request.slack_api_key)),
            ],
        )
    except OnboardingFailedError as e:
        onboarding_failed_report(e)
    else:
        onboarding_success_report(employee)


if __name__ == "__main__":
    main(sys.argv[1:])
