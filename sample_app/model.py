import abc
import dataclasses
from typing import Optional, List, Union


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


class OnboardingStep(abc.ABC):
    @property
    @abc.abstractmethod
    def interrupts_flow(self) -> bool:
        """Indicates if the step fails should latter steps be processed"""
        ...

    @abc.abstractmethod
    def run(self, employee: Employee):
        ...

    def __str__(self):
        return type(self).__name__


class OnboardingFailedError(Exception):
    def __init__(
        self,
        failed_steps: Union[List[OnboardingStep], List[str]],
        unprocessed_steps: Union[List[OnboardingStep], List[str]],
        employee: Employee,
    ):
        self.failed_steps = failed_steps
        self.unprocessed_steps = unprocessed_steps
        self.employee = employee
