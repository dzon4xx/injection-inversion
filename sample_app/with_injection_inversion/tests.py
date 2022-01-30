from unittest.mock import Mock, sentinel

import pytest


from with_injection_inversion.main import (
    onboard,
    main,
    CreateGmailAccount,
    CreateSlackAccount,
    CreateJiraAccount,
    SendInvitationEmail,
)

from model import (
    Employee,
    OnboardingStep,
    OnboardingFailedError,
    StepProcessingError,
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
        # Given
        step_1 = Mock(spec_set=OnboardingStep, interrupts_flow=False)
        step_2 = Mock(spec_set=OnboardingStep, interrupts_flow=False)

        # When
        onboard(employee, [step_1, step_2])

        # Then
        step_1.run.assert_called_once_with(employee)
        step_2.run.assert_called_once_with(employee)

    def test_first_step_which_interrupts_flow_fails__error_raised(
        self, employee: Employee
    ):
        # Given
        step_1 = Mock(
            spec_set=OnboardingStep,
            run=Mock(side_effect=StepProcessingError),
            interrupts_flow=True,
        )
        step_2 = Mock(spec_set=OnboardingStep, interrupts_flow=False)

        with pytest.raises(OnboardingFailedError) as e:
            # When
            onboard(employee, [step_1, step_2])

        # Then
        exc: OnboardingFailedError = e.value
        assert exc.failed_steps == [step_1]
        assert exc.unprocessed_steps == [step_2]
        step_1.run.assert_called_once_with(employee)
        step_2.run.assert_not_called()

    def test_first_step_which_doesnt_interrupt_flow_fails__error_raised(
        self, employee: Employee
    ):
        # Given
        step_1 = Mock(
            spec_set=OnboardingStep,
            run=Mock(side_effect=StepProcessingError),
            interrupts_flow=False,
        )
        step_2 = Mock(spec_set=OnboardingStep, interrupts_flow=False)

        with pytest.raises(OnboardingFailedError) as e:
            # When
            onboard(employee, [step_1, step_2])

        # Then
        exc: OnboardingFailedError = e.value
        assert exc.failed_steps == [step_1]
        assert exc.unprocessed_steps == []
        step_1.run.assert_called_once_with(employee)
        step_2.run.assert_called_once_with(employee)


class TestCreateGmailAccount:
    def test_run_success(self):
        # Given
        employee = Employee.new("Bob", "Smith")
        domain = "stxnext.pl"

        mock_client = Mock(
            spec_set=GmailClient, register=Mock(return_value=sentinel.email)
        )
        # When
        CreateGmailAccount(mock_client, domain).run(employee)

        # Then
        mock_client.register.assert_called_once_with(prefix="bob.smith", domain=domain)
        assert employee.email == sentinel.email

    def test_run_failure(self, employee: Employee):
        # Given
        mock_client = Mock(
            spec_set=GmailClient, register=Mock(side_effect=GmailException)
        )
        with pytest.raises(StepProcessingError) as exc_info:
            # When
            CreateGmailAccount(mock_client, "stxnext.pl").run(employee)

        # Then
        assert str(exc_info.value) == "Creating gmail account failed"
        assert employee.email is None


class TestCreateSlackAccount:
    def test_run_success(self):
        # Given
        employee = Employee.new("Bob", "Smith")

        mock_client = Mock(spec_set=SlackClient, new_account=Mock())
        # When
        CreateSlackAccount(mock_client).run(employee)

        # Then
        mock_client.new_account.assert_called_once_with(user="bob.smith", email=None)

    def test_run_failure(self, employee: Employee):
        # Given
        mock_client = Mock(
            spec_set=SlackClient, new_account=Mock(side_effect=SlackException)
        )
        with pytest.raises(StepProcessingError) as exc_info:
            # When
            CreateSlackAccount(mock_client).run(employee)

        # Then
        assert str(exc_info.value) == "Creating slack account failed"


class TestCreateJiraAccount:
    def test_run_success(self):
        # Given
        employee = Employee.new("Bob", "Smith")

        mock_client = Mock(spec_set=JiraClient, create_account=Mock())
        # When
        CreateJiraAccount(mock_client).run(employee)

        # Then
        mock_client.create_account.assert_called_once_with(
            email=None, user_name="bob.s"
        )

    def test_run_failure(self, employee: Employee):
        # Given
        mock_client = Mock(
            spec_set=JiraClient, create_account=Mock(side_effect=JiraException)
        )
        with pytest.raises(StepProcessingError) as exc_info:
            # When
            CreateJiraAccount(mock_client).run(employee)

        # Then
        assert str(exc_info.value) == "Creating jira account failed"


class TestSendInvitationEmail:
    def test_run_success(self):
        # Given
        employee = Employee.new("Bob", "Smith")
        employee.set_email("bob@smith.com")

        mock_client = Mock(spec_set=GmailClient, send_email=Mock())
        # When
        SendInvitationEmail(mock_client).run(employee)

        # Then
        mock_client.send_email.assert_called_once_with(
            to="bob@smith.com",
            title="Welcome onboard!",
            body=f"We are happy to have you with us Bob",
        )

    def test_run_failure(self, employee: Employee):
        # Given
        employee.set_email("bob@smith.com")
        mock_client = Mock(
            spec_set=GmailClient, send_email=Mock(side_effect=GmailException)
        )
        with pytest.raises(StepProcessingError) as exc_info:
            # When
            SendInvitationEmail(mock_client).run(employee)

        assert str(exc_info.value) == "Sending email failed"

        mock_client.send_email.assert_called_once_with(
            to="bob@smith.com",
            title="Welcome onboard!",
            body=f"We are happy to have you with us Bob",
        )


class TestCliIntegration:
    def test_happy_path(self, capsys):
        # When
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

        # Then
        assert capsys.readouterr().out.rstrip().split("\n") == [
            "Gmail account was successfully created. email='bob.smith@stxnext.pl'",
            "Jira account was successfully created. user_name='bob.s' user_name: email='bob.smith@stxnext.pl'",
            "Slack account was successfully created. user='bob.smith' user_name: email='bob.smith@stxnext.pl'",
            "Sending email to='bob.smith@stxnext.pl' title='Welcome onboard!' body='We are happy to have you with us Bob'",
            "Employee onboarding successfull. name='Bob' surname='Smith' email='bob.smith@stxnext.pl'",
        ]

    def test_failure_path(self, capsys):
        # When
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

        # Then
        assert capsys.readouterr().out.rstrip().split("\n") == [
            "Employee onboarding failed. name='Bob' surname='Smith' "
            "failed_steps='CreateGmailAccount' unprocessed_steps='CreateJiraAccount, "
            "CreateSlackAccount, SendInvitationEmail'"
        ]
