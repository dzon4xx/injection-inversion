from typing import Optional


class Client:
    def __init__(self, api_key: str, is_test: bool):
        self._api_key = api_key
        self._is_test = is_test

    def send_request(self):
        print("Sending message to api")


client: Optional[Client] = None


def client_locator() -> Client:
    global client
    return client


class Service:
    def run(self):
        client = client_locator()
        client.send_request()


def main():
    global client
    config = dict(is_test=True, api_key="qwerty")

    client = Client(
        is_test=config["is_test"],
        api_key=config["api_key"],
    )
    Service().run()
