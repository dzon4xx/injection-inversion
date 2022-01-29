from dataclasses import dataclass
from typing import List


@dataclass
class Product:
    price: int


@dataclass
class Order:
    id: int

    def products(self) -> List[Product]:
        return [Product(20), Product(30), Product(40)]

    @classmethod
    def get_by_id(cls, id_: int):
        return Order(id_)
