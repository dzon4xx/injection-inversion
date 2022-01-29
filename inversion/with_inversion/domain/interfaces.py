import abc


class PaymentGatewayClient(abc.ABC):

    @abc.abstractmethod
    def charge(self, user: int, amount: int):
        ...
