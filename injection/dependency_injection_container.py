import os
from unittest import mock

from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject


class Client:
    def __init__(self, api_key: str, is_test: bool):
        self._api_key = api_key
        self._is_test = is_test

    def send_request(self):
        print("Sending message to api")


class Service:
    def __init__(self, client: Client):
        self._client: Client = client

    def run(self):
        self._client.send_request()


class Container(containers.DeclarativeContainer):

    config = providers.Configuration()

    client = providers.Singleton(
        Client,
        api_key=config.api_key,
        is_test=config.is_test,
    )

    service = providers.Factory(
        Service,
        client=client,
    )


@inject
def main(service: Service = Provide[Container.service]):
    service.run()


if __name__ == "__main__":
    os.environ["API_KEY"] = "1234"
    container = Container()
    container.config.api_key.from_env("API_KEY", required=True)
    container.config.is_test.from_env("IS_TEST", as_=bool, default=False)
    container.wire(modules=[__name__])

    main()  # <-- dependency is injected automatically

    with container.client.override(mock.Mock()):
        main()  # <-- overridden dependency is injected automatically
