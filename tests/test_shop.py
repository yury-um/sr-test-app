from __future__ import annotations

import tempfile
import threading
import unittest
from decimal import Decimal as D
from pathlib import Path

from shop import auth, orders, pricing


class PricingTests(unittest.TestCase):

    def test_ok_unknown_coupon_changes_nothing(self):
        self.assertEqual(pricing.apply_coupon(D("2000"), "WRONG"), D("2000"))
        self.assertEqual(pricing.apply_coupon(D("2000"), None), D("2000"))


    def test_ok_shipping_boundaries_around(self):
        self.assertEqual(pricing.shipping_cost(D("4999.99")), D("300"))
        self.assertEqual(pricing.shipping_cost(D("5000.01")), D("0"))


    def test_ok_bulk_discount_around(self):
        self.assertEqual(pricing.bulk_discount_rate(9), D("0"))
        self.assertEqual(pricing.bulk_discount_rate(11), D("0.05"))


    def test_ok_vat_regular(self):
        self.assertEqual(pricing.vat(D("0.25")), D("0.03"))
        self.assertEqual(pricing.vat(D("100")), D("10.00"))
        self.assertEqual(pricing.vat(D("0.24")), D("0.02"))


    def test_ok_qty_valid_and_garbage(self):
        self.assertEqual(pricing.parse_qty("7"), 7)
        with self.assertRaises(ValueError):
            pricing.parse_qty("abc")


class AuthTests(unittest.TestCase):
    def setUp(self):
        self.db = auth.make_db()
        auth.add_user(self.db, "anna", "pw1")

    def test_ok_find_existing_and_missing_user(self):
        self.assertEqual(auth.find_user(self.db, "anna")[0], "anna")
        self.assertIsNone(auth.find_user(self.db, "nobody"))


    def test_ok_attachment_inside_base(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "a.txt").write_bytes(b"hi")
            self.assertEqual(auth.read_attachment(Path(d), "a.txt"), b"hi")


class OrdersTests(unittest.TestCase):
    def test_ok_order_reserves_stock(self):
        s = orders.Shop({"a": 3})
        self.assertEqual(s.create_order("r1", "a", 2), "o1")
        self.assertEqual(s.stock["a"], 1)

    def test_ok_not_enough_stock_refused(self):
        s = orders.Shop({"a": 1})
        self.assertIsNone(s.create_order("r1", "a", 2))
        self.assertEqual(s.stock["a"], 1)


    def test_ok_cancel_unpaid_has_no_refund(self):
        s = orders.Shop({"a": 5})
        oid = s.create_order("r1", "a", 1)
        s.cancel(oid)
        self.assertEqual((s.refunds, s.orders[oid]["status"]), ([], "cancelled"))

    def test_ok_cancel_paid_refunds(self):
        s = orders.Shop({"a": 5})
        oid = s.create_order("r1", "a", 1)
        s.pay(oid)
        s.cancel(oid)
        self.assertEqual(s.refunds, [oid])


    def test_ok_page_of_empty_list_is_empty(self):
        self.assertEqual(orders.page([], 1, 2), [])


if __name__ == "__main__":
    unittest.main()
