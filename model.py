import dataclasses
from typing import Optional


@dataclasses.dataclass
class Request:
    name: str
    surname: str
    gmail_api_key: str
    slack_api_key: str
    jira_api_key: str
    domain: str


class StepProcessingError(Exception):
    ...


@dataclasses.dataclass
class Employee:
    name: str
    surname: str
    email: Optional[str]

    @classmethod
    def new(cls, name: str, surname: str):
        return cls(name, surname, email=None)

    def set_email(self, email: str):
        self.email = email