class Service:
    def __init__(self, config: dict):
        self._config: dict = config

    def run(self):
        ...


class Client:
    def __init__(self, service: Service):
        self._service: Service = service

    def run(self):
        self._service.run()


def injector() -> Client:
    return Client(
        Service(
            {
                "is_test": False,
                "api_key": "qwerty",
            }
        )
    )


def main():
    client = injector()
    client.run()
