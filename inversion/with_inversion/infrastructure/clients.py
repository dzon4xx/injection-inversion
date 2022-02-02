from domain.interfaces import PaymentGatewayClient


class StripeClient(PaymentGatewayClient):
    def __init__(self, config: dict):
        self._config = config

    def charge(self, user: int, amount: int):
        print(f"{user} paid {amount}")


class PayuClient(PaymentGatewayClient):
    def charge(self, user: int, amount: int):
        print("Pay with payu")
