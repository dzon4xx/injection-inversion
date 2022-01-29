class StripeClient:
    def __init__(self, config: dict):
        self._config = config

    def charge(self, user: int, amount: int):
        print(f"{user} paid {amount}")
