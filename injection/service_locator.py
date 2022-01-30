from typing import Optional


class Service:
    def __init__(self, config: dict):
        self._config: dict = config

    def run(self):
        ...


service: Optional[Service] = None


def service_locator() -> Service:
    global service
    return service


class Client:
    def run(self):
        service = service_locator()
        service.run()


def main():
    global service
    service = Service(
        {
            "is_test": True,
            "api_key": "qwerty",
        }
    )
    Client().run()
