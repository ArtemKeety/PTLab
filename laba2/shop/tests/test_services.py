from decimal import Decimal

from django.test import SimpleTestCase

from shop.services import apply_discount


class ApplyDiscountTests(SimpleTestCase):
    def test_zero_discount_keeps_price(self):
        self.assertEqual(apply_discount(1000, 0), Decimal('1000.00'))

    def test_none_and_empty_discount_mean_zero(self):
        self.assertEqual(apply_discount(1000, None), Decimal('1000.00'))
        self.assertEqual(apply_discount(1000, ''), Decimal('1000.00'))

    def test_basic_percent(self):
        self.assertEqual(apply_discount(1000, 10), Decimal('900.00'))

    def test_full_discount(self):
        self.assertEqual(apply_discount(1000, 100), Decimal('0.00'))

    def test_half_discount(self):
        self.assertEqual(apply_discount(200, 50), Decimal('100.00'))

    def test_accepts_decimal_and_string_price(self):
        self.assertEqual(apply_discount(Decimal('10.50'), 10), Decimal('9.45'))
        self.assertEqual(apply_discount('1000', 10), Decimal('900.00'))

    def test_rounds_half_up_to_kopecks(self):
        # 1 * 12.5% = 0.125 -> 0.13, а не банковские 0.12
        self.assertEqual(apply_discount(1, Decimal('87.5')), Decimal('0.13'))

    def test_fractional_percent_is_not_truncated_to_rubles(self):
        # 999 * 10% = 899.10; целочисленное деление дало бы 900
        self.assertEqual(apply_discount(999, 10), Decimal('899.10'))
