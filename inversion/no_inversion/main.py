from clients import StripeClient
from services import pay_for_an_order


def main():
    pay_for_an_order(
        user_id=1, order_id=2, payment_gateway=StripeClient({"api_key": "asdf"})
    )


if __name__ == "__main__":
    main()
