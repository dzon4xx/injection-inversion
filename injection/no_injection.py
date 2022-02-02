class Client:
    def __init__(self, api_key: str, is_test: bool):
        self._api_key = api_key
        self._is_test = is_test

    def send_request(self):
        print("Sending message to api")


class Service:
    def run(self):
        # Wyobraźmy sobie, że tutaj odczytywany jest config np z pliku.
        config = dict(is_test=True, api_key="qwerty")
        client = Client(
            api_key=config["api_key"],
            is_test=config["is_test"],
        )
        client.send_request()


def main():
    Service().run()


if __name__ == "__main__":
    main()
