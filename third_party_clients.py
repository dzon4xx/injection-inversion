import time


class JiraException(Exception):
    ...


class JiraClient:

    def __init__(self, api_key: str):
        self._api_key = api_key

    def create_account(self, email: str, user_name: str):
        if "INVALID" in self._api_key:
            raise JiraException("Invalid api key")
        time.sleep(1)
        print(f"Jira account was successfully created. {user_name=} user_name: {email=}")


class SlackException(Exception):
    ...


class SlackClient:
    def __init__(self, api_key: str):
        self._api_key = api_key

    def new_account(self, user: str, email: str):
        if "INVALID" in self._api_key:
            raise SlackException("Invalid api key")
        time.sleep(1)
        print(f"Slack account was successfully created. {user=} user_name: {email=}")


class GmailException(Exception):
    ...


class GmailClient:
    def __init__(self, api_key: str):
        self._api_key = api_key

    def register(self, prefix: str, domain: str) -> str:
        if "INVALID" in self._api_key:
            raise GmailException("Invalid api key")
        email = f"{prefix}@{domain}"
        time.sleep(1)
        print(f"Gmail account was successfully created. {email=}")
        return email
