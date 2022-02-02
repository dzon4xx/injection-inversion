from entities import Order
from clients import StripeClient


def pay_for_an_order(user_id: int, order_id: int, payment_gateway: StripeClient):
    order = Order.get_by_id(order_id)
    total_amount: int = sum(product.price for product in order.products())
    payment_gateway.charge(user_id, total_amount)
