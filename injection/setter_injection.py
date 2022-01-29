from typing import Optional


class Service:

    def __init__(self):
        self._config: Optional[dict] = None

    def set_config(self, config: dict):
        self._config = config

    def run(self):
        ...


def client(service: Service):
    service.run()


def injector():
    config = {
        "is_test": False,
        "api_key": "qwerty",
    }
    service = Service()
    service.set_config(config)
    client(service)
