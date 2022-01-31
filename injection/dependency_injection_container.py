import os
from unittest import mock

from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject


class ApiClient:
    def __init__(self, api_key: str, timeout: int):
        self._api_key = api_key
        self._timeout = timeout

    def send(self):
        print("Sending message to api")


class Service:
    def __init__(self, api_client: ApiClient):
        self._api_client: ApiClient = api_client

    def run(self):
        self._api_client.send()


class Container(containers.DeclarativeContainer):

    config = providers.Configuration()

    api_client = providers.Singleton(
        ApiClient,
        api_key=config.api_key,
        timeout=config.timeout,
    )

    service = providers.Factory(
        Service,
        api_client=api_client,
    )


@inject
def main(service: Service = Provide[Container.service]):
    service.run()


if __name__ == "__main__":
    os.environ["API_KEY"] = "1234"
    container = Container()
    container.config.api_key.from_env("API_KEY", required=True)
    container.config.timeout.from_env("TIMEOUT", as_=int, default=5)
    container.wire(modules=[__name__])

    main()  # <-- dependency is injected automatically

    with container.api_client.override(mock.Mock()):
        main()  # <-- overridden dependency is injected automatically
