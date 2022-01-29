from domain.entities import Order
from domain.interfaces import PaymentGatewayClient


def pay_for_a_product(user_id: int, order_id: int, payment_gateway: PaymentGatewayClient):
    order = Order.get_by_id(order_id)
    total_amount: int = sum(product.price for product in order.products())
    payment_gateway.charge(user_id, total_amount)
