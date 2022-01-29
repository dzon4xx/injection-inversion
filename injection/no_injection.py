class Service:

    def __init__(self, config: dict):
        self._config: dict = config

    def run(self):
        ...


class Client:
    def run(self, is_test: bool, api_key: str):
        service = Service({
            "is_test": is_test,
            "api_key": api_key,
        })
        service.run()


def main():
    Client().run(is_test=True, api_key="qwerty")
