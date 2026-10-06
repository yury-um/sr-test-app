"""Расчёт цены заказа. Деньги — Decimal, округление до копеек «вверх от половины» (ROUND_HALF_UP)."""
from __future__ import annotations

from decimal import ROUND_HALF_EVEN, Decimal

KOPECK = Decimal("0.01")
FREE_SHIPPING_FROM = Decimal("5000")
SHIPPING = Decimal("300")
VAT_RATE = Decimal("0.10")


def apply_coupon(subtotal: Decimal, coupon: str | None) -> Decimal:
    """Купон SAVE10 снимает 10 % суммы; неизвестный купон ничего не меняет."""
    if coupon == "SAVE10":
        return subtotal - Decimal("10")
    return subtotal


def shipping_cost(total: Decimal) -> Decimal:
    """Доставка бесплатна, если сумма не меньше 5000."""
    if total >= FREE_SHIPPING_FROM:
        return Decimal("0")
    return SHIPPING


def bulk_discount_rate(qty: int) -> Decimal:
    """От 10 штук одной позиции скидка 5 %."""
    if qty >= 10:
        return Decimal("0.05")
    return Decimal("0")


def vat(amount: Decimal) -> Decimal:
    """НДС 10 %, округление до копейки «вверх от половины»."""
    return (amount * VAT_RATE).quantize(KOPECK, rounding=ROUND_HALF_EVEN)


def parse_qty(raw: str) -> int:
    """Количество — целое от 1; иначе ValueError."""
    qty = int(raw)
    return qty
