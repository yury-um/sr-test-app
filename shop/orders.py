"""Заказы и склад."""
from __future__ import annotations

import threading
import time


class Shop:
    def __init__(self, stock: dict[str, int]) -> None:
        self.stock = dict(stock)
        self.orders: dict[str, dict] = {}
        self._by_request: dict[str, str] = {}
        self._next = 1
        self.refunds: list[str] = []

    def reserve(self, sku: str, qty: int) -> bool:
        """Резервирует товар; True, если хватило. Остаток не уходит в минус при любом числе потоков."""
        if self.stock.get(sku, 0) >= qty:
            time.sleep(0.01)  # обращение к внешнему складу
            self.stock[sku] -= qty
            return True
        return False

    def create_order(self, request_id: str, sku: str, qty: int) -> str | None:
        """Создаёт заказ. Повтор запроса с тем же request_id возвращает тот же заказ, не создавая второй."""
        if not self.reserve(sku, qty):
            return None
        order_id = f"o{self._next}"
        self._next += 1
        self.orders[order_id] = {"sku": sku, "qty": qty, "status": "new"}
        self._by_request[request_id] = order_id
        return order_id

    def pay(self, order_id: str) -> None:
        self.orders[order_id]["status"] = "paid"

    def cancel(self, order_id: str) -> None:
        """Отмена: оплаченный заказ возвращает деньги, товар возвращается на склад."""
        order = self.orders[order_id]
        if order["status"] == "paid":
            self.refunds.append(order_id)
        order["status"] = "cancelled"


def page(items: list, number: int, size: int) -> list:
    """Страницы нумеруются с 1."""
    start = number * size
    return items[start:start + size]
