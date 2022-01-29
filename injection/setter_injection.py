from typing import Optional


class Service:
    def __init__(self, config: dict):
        self._config: dict = config

    def run(self):
        ...


class Client:
    def __init__(self):
        self._service: Optional[Service] = None

    def set_service(self, service: Service):
        self._service = service

    def run(self):
        self._service.run()


def injector() -> Client:
    client = Client()
    client.set_service(
        Service(
            {
                "is_test": False,
                "api_key": "qwerty",
            }
        )
    )
    return client


def main():
    client = injector()
    client.run()
