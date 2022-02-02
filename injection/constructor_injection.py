class Client:
    def __init__(self, api_key: str, is_test: bool):
        self._api_key = api_key
        self._is_test = is_test

    def send_request(self):
        print("Sending message to api")


class Service:
    def __init__(self, service: Client):
        self._client: Client = service

    def run(self):
        self._client.send_request()


def injector() -> Service:
    config = dict(is_test=True, api_key="qwerty")
    return Service(
        Client(
            is_test=config["is_test"],
            api_key=config["api_key"],
        )
    )


def main():
    service = injector()
    service.run()


if __name__ == "__main__":
    main()
