import dataclasses
from unittest.mock import patch, Mock, sentinel

import pytest

from model import Request, OnboardingFailedError, Employee
from third_party_clients import (
    GmailException,
    GmailClient,
    SlackClient,
    SlackException,
    JiraClient,
    JiraException,
)
from without_injection_inversion.main import (
    main,
    onboard,
)


@dataclasses.dataclass
class MockedClients:
    gmail: Mock
    jira: Mock
    slack: Mock


class TestOnboard:
    @pytest.fixture
    def mock_clients(self) -> MockedClients:
        clients = MockedClients(
            gmail=Mock(
                spec_set=GmailClient, register=Mock(return_value=sentinel.email)
            ),
            jira=Mock(spec_set=JiraClient, create_account=Mock()),
            slack=Mock(spec_set=SlackClient, new_account=Mock()),
        )

        with patch(
            "third_party_clients.GmailClient", new=lambda *args, **kwargs: clients.gmail
        ), patch(
            "third_party_clients.JiraClient", new=lambda *args, **kwargs: clients.jira
        ), patch(
            "third_party_clients.SlackClient", new=lambda *args, **kwargs: clients.slack
        ):
            yield clients

    @pytest.fixture
    def request_(self) -> Request:
        return Request(
            name="Bob",
            surname="Smith",
            gmail_api_key="gmail-api-key",
            slack_api_key="slack-api-key",
            jira_api_key="jira-api-key",
            domain="stxnext.pl",
        )

    @pytest.fixture
    def employee(self) -> Employee:
        return Employee.new("Bob", "Smith")

    def test_success(
        self, employee: Employee, request_: Request, mock_clients: MockedClients
    ):
        # When
        onboard(employee, request_)

        # Then
        mock_clients.gmail.register.assert_called_once_with(
            prefix="bob.smith", domain=request_.domain
        )
        mock_clients.jira.create_account.assert_called_once_with(
            email=sentinel.email, user_name="bob.s"
        )
        mock_clients.slack.new_account.assert_called_once_with(
            user="bob.smith", email=sentinel.email
        )
        assert employee.email == sentinel.email

    def test_gmail_call_failed__process_interrupted(
        self, employee: Employee, request_: Request, mock_clients: MockedClients
    ):
        # Given
        mock_clients.gmail.register.side_effect = GmailException
        with pytest.raises(OnboardingFailedError) as exc_info:
            # When
            onboard(employee, request_)

        # Then
        exc: OnboardingFailedError = exc_info.value
        assert exc.failed_steps == ["CreateGmailAccount"]
        assert exc.unprocessed_steps == ["CreateJiraAccount", "CreateSlackAccount"]

        mock_clients.gmail.register.assert_called_once_with(
            prefix="bob.smith", domain=request_.domain
        )
        mock_clients.jira.create_account.assert_not_called()
        mock_clients.slack.new_account.assert_not_called()
        assert employee.email is None

    def test_jira_call_failed__process_uninterrupted(
        self, employee: Employee, request_: Request, mock_clients: MockedClients
    ):
        # Given
        mock_clients.jira.create_account.side_effect = JiraException
        with pytest.raises(OnboardingFailedError) as exc_info:
            # When
            onboard(employee, request_)

        # Then
        exc: OnboardingFailedError = exc_info.value
        assert exc.failed_steps == ["CreateJiraAccount"]
        assert exc.unprocessed_steps == ["CreateSlackAccount"]

        mock_clients.gmail.register.assert_called_once_with(
            prefix="bob.smith", domain=request_.domain
        )
        mock_clients.jira.create_account.assert_called_once_with(
            email=sentinel.email, user_name="bob.s"
        )
        mock_clients.slack.new_account.assert_called_once_with(
            user="bob.smith", email=sentinel.email
        )
        assert employee.email is sentinel.email

    def test_slack_call_failed__process_uninterrupted(
        self, employee: Employee, request_: Request, mock_clients: MockedClients
    ):
        # Given
        mock_clients.slack.new_account.side_effect = SlackException
        with pytest.raises(OnboardingFailedError) as exc_info:
            # When
            onboard(employee, request_)

        # Then
        exc: OnboardingFailedError = exc_info.value
        assert exc.failed_steps == ["CreateSlackAccount"]
        assert exc.unprocessed_steps == []

        mock_clients.gmail.register.assert_called_once_with(
            prefix="bob.smith", domain=request_.domain
        )
        mock_clients.jira.create_account.assert_called_once_with(
            email=sentinel.email, user_name="bob.s"
        )
        mock_clients.slack.new_account.assert_called_once_with(
            user="bob.smith", email=sentinel.email
        )
        assert employee.email is sentinel.email


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
            "CreateSlackAccount'"
        ]
