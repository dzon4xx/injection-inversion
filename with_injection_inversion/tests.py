from unittest.mock import Mock, sentinel

import pytest


from with_injection_inversion.main import (
    onboard,
    Employee,
    OnboardingStep,
    OnboardingFailed,
    StepProcessingError,
    CreateGmailAccount,
    main,
    CreateSlackAccount,
    CreateJiraAccount,
)
from third_party_clients import (
    GmailClient,
    GmailException,
    SlackClient,
    SlackException,
    JiraClient,
    JiraException,
)


@pytest.fixture
def employee():
    return Employee.new("Bob", "Smith")


class TestOnboard:
    def test_all_steps_successfull(self, employee: Employee):
        step_1 = Mock(spec_set=OnboardingStep, interrupts_flow=False)
        step_2 = Mock(spec_set=OnboardingStep, interrupts_flow=False)

        onboard(employee, [step_1, step_2])

        step_1.run.assert_called_once_with(employee)
        step_2.run.assert_called_once_with(employee)

    def test_first_step_which_interrupts_flow_fails__error_raised(
        self, employee: Employee
    ):
        step_1 = Mock(
            spec_set=OnboardingStep,
            run=Mock(side_effect=StepProcessingError),
            interrupts_flow=True,
        )
        step_2 = Mock(spec_set=OnboardingStep, interrupts_flow=False)

        with pytest.raises(OnboardingFailed) as e:
            onboard(employee, [step_1, step_2])

        exc: OnboardingFailed = e.value
        assert exc.failed_steps == [step_1]
        assert exc.unprocessed_steps == [step_2]
        step_1.run.assert_called_once_with(employee)
        step_2.run.assert_not_called()

    def test_first_step_which_doesnt_interrupt_flow_fails__error_raised(
        self, employee: Employee
    ):
        step_1 = Mock(
            spec_set=OnboardingStep,
            run=Mock(side_effect=StepProcessingError),
            interrupts_flow=False,
        )
        step_2 = Mock(spec_set=OnboardingStep, interrupts_flow=False)

        with pytest.raises(OnboardingFailed) as e:
            onboard(employee, [step_1, step_2])

        exc: OnboardingFailed = e.value
        assert exc.failed_steps == [step_1]
        assert exc.unprocessed_steps == []
        step_1.run.assert_called_once_with(employee)
        step_2.run.assert_called_once_with(employee)


class TestCreateGmailAccount:
    def test_run_success(self):
        employee = Employee.new("Bob", "Smith")
        domain = "stxnext.pl"

        mock_client = Mock(
            spec_set=GmailClient, register=Mock(return_value=sentinel.email)
        )
        CreateGmailAccount(mock_client, domain).run(employee)

        mock_client.register.assert_called_once_with(prefix="bob.smith", domain=domain)
        assert employee.email == sentinel.email

    def test_run_failure(self, employee: Employee):
        mock_client = Mock(
            spec_set=GmailClient, register=Mock(side_effect=GmailException)
        )
        with pytest.raises(StepProcessingError):
            CreateGmailAccount(mock_client, "stxnext.pl").run(employee)


class TestCreateSlackAccount:
    def test_run_success(self, employee):
        employee = Employee.new("Bob", "Smith")

        mock_client = Mock(spec_set=SlackClient, new_account=Mock())
        CreateSlackAccount(mock_client).run(employee)

        mock_client.new_account.assert_called_once_with(user="bob.smith", email=None)

    def test_run_failure(self, employee: Employee):
        mock_client = Mock(
            spec_set=SlackClient, new_account=Mock(side_effect=SlackException)
        )
        with pytest.raises(StepProcessingError):
            CreateSlackAccount(mock_client).run(employee)


class TestCreateJiraAccount:
    def test_run_success(self):
        employee = Employee.new("Bob", "Smith")

        mock_client = Mock(spec_set=JiraClient, create_account=Mock())
        CreateJiraAccount(mock_client).run(employee)

        mock_client.create_account.assert_called_once_with(
            email=None, user_name="bob.s"
        )

    def test_run_failure(self, employee: Employee):
        mock_client = Mock(
            spec_set=JiraClient, create_account=Mock(side_effect=JiraException)
        )
        with pytest.raises(StepProcessingError):
            CreateJiraAccount(mock_client).run(employee)


class TestCliIntegration:
    def test_happy_path(self, capsys):
        main(
            [
                "--name",
                "Bob",
                "--surname",
                "Smith",
                "--gmail-api-key",
                "some-gmail-key",
                "--jira-api-key",
                "some-jira-key",
                "--slack-api-key",
                "some-slack-key",
            ]
        )

        assert capsys.readouterr().out.rstrip().split("\n") == [
            "Gmail account was successfully created. email='bob.smith@stxnext.pl'",
            "Jira account was successfully created. user_name='bob.s' user_name: email='bob.smith@stxnext.pl'",
            "Slack account was successfully created. user='bob.smith' user_name: email='bob.smith@stxnext.pl'",
            "Employee onboarding successfull. name='Bob' surname='Smith' email='bob.smith@stxnext.pl'",
        ]

    def test_failure_path(self, capsys):
        main(
            [
                "--name",
                "Bob",
                "--surname",
                "Smith",
                "--gmail-api-key",
                "INVALID-gmail-key",
                "--jira-api-key",
                "some-jira-key",
                "--slack-api-key",
                "some-slack-key",
            ]
        )

        assert capsys.readouterr().out.rstrip().split("\n") == [
            "Employee onboarding failed. name='Bob' surname='Smith' "
            "failed_steps='CreateGmailAccount' unprocessed_steps='CreateJiraAccount, "
            "CreateSlackAccount'"
        ]
