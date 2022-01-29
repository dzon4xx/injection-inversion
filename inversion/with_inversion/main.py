from infrastructure.clients import StripeClient
from domain.services import pay_for_a_product


def main():
    pay_for_a_product(
        user_id=1, order_id=2, payment_gateway=StripeClient({"api_key": "asdf"})
    )


if __name__ == "__main__":
    main()
