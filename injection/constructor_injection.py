class Service:

    def __init__(self, config: dict):
        self._config: dict = config

    def run(self):
        ...


def client(service: Service):
    service.run()


def injector():
    config = {
        "is_test": False,
        "api_key": "qwerty",
    }
    client(Service(config))
