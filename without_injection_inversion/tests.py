from unittest.mock import patch, Mock, sentinel

import pytest

from model import StepProcessingError
from third_party_clients import GmailException, GmailClient, SlackClient, \
    SlackException, JiraClient, JiraException
from without_injection_inversion.main import (
    main,
    Employee,
    create_gmail_account, create_slack_account, create_jira_account,
)


@pytest.fixture
def employee() -> Employee:
    return Employee.new("Bob", "Smith")


@pytest.fixture
def api_key() -> str:
    return "api-key"


class TestCreateGmailAccount:
    def test_run_success(self, api_key: str):
        employee = Employee.new("Bob", "Smith")
        domain = "stxnext.pl"

        mock_client = Mock(spec_set=GmailClient, register=Mock(return_value=sentinel.email))
        # TODO clients are patched on third_party_clients module because they are
        #  used as third_party_clients.GmailClient in client code.
        with patch("third_party_clients.GmailClient", Mock(return_value=mock_client)):
            create_gmail_account(employee, domain, api_key)

        mock_client.register.assert_called_once_with(prefix="bob.smith", domain=domain)
        assert employee.email == sentinel.email

    def test_run_failure(self, employee: Employee, api_key: str):
        domain = "stxnext.pl"
        mock_client = Mock(spec_set=GmailClient, register=Mock(side_effect=GmailException))
        with patch(
            "third_party_clients.GmailClient", Mock(return_value=mock_client)
        ), pytest.raises(StepProcessingError):
            create_gmail_account(employee, domain, api_key)


class TestCreateSlackAccount:
    def test_run_success(self, employee, api_key: str):
        employee = Employee.new("Bob", "Smith")
        mock_client = Mock(spec_set=SlackClient, new_account=Mock())

        with patch("third_party_clients.SlackClient", Mock(return_value=mock_client)):
            create_slack_account(employee, api_key)

        mock_client.new_account.assert_called_once_with(user="bob.smith", email=None)

    def test_run_failure(self, employee: Employee, api_key: str):
        mock_client = Mock(spec_set=SlackClient, new_account=Mock(side_effect=SlackException))

        with patch(
                "third_party_clients.SlackClient", Mock(return_value=mock_client)
        ), pytest.raises(StepProcessingError):
            create_slack_account(employee, api_key)


class TestCreateJiraAccount:
    def test_run_success(self, api_key: str):
        employee = Employee.new("Bob", "Smith")

        mock_client = Mock(spec_set=JiraClient, create_account=Mock())
        with patch("third_party_clients.JiraClient", Mock(return_value=mock_client)):
            create_jira_account(employee, api_key)

        mock_client.create_account.assert_called_once_with(
            email=None, user_name="bob.s"
        )

    def test_run_failure(self, employee: Employee, api_key: str):
        mock_client = Mock(
            spec_set=JiraClient, create_account=Mock(side_effect=JiraException)
        )

        with patch("third_party_clients.JiraClient", Mock(return_value=mock_client)), pytest.raises(StepProcessingError):
            create_jira_account(employee, api_key)


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
