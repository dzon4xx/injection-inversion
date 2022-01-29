class Service:

    def __init__(self, config: dict):
        self._config: dict = config

    def run(self):
        ...


def client(is_test, api_key):
    config = {
        "is_test": is_test,
        "api_key": api_key,
    }
    service = Service(config)
    service.run()


def injector():
    client(is_test=True, api_key="qwerty")
