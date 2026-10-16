from decimal import Decimal

from django.db.models import ProtectedError
from django.test import TestCase
from django.utils import timezone

from shop.models import CustomUser, Product, Purchase


class ProductModelTest(TestCase):
    """Тесты модели Product."""

    def setUp(self):
        self.product = Product.objects.create(name='Книга', price=1000)

    def test_str(self):
        self.assertEqual(str(self.product), 'Книга')

    def test_default_price_field(self):
        self.assertEqual(self.product.price, 1000)

    def test_price_with_discount_returns_int(self):
        """Целочисленное деление цены и процента даёт int."""
        result = self.product.price_with_discount(10)
        self.assertIsInstance(result, int)
        self.assertEqual(result, 900)

    def test_price_with_discount_basic(self):
        # 1000 - 1000 * 10 // 100 = 1000 - 100 = 900.0
        self.assertEqual(self.product.price_with_discount(10), 900.0)

    def test_price_with_discount_zero(self):
        self.assertEqual(self.product.price_with_discount(0), 1000.0)

    def test_price_with_discount_full(self):
        self.assertEqual(self.product.price_with_discount(100), 0.0)

    def test_price_with_discount_integer_division_truncates(self):
        """Из-за // скидка округляется вниз до целых единиц цены."""
        product = Product.objects.create(name='Ручка', price=999)
        # 999 * 10 // 100 = 99  -> 999 - 99 = 900.0
        # «Честное» значение было бы 899.1
        self.assertEqual(product.price_with_discount(10), 900.0)


class CustomUserModelTest(TestCase):
    """Тесты модели CustomUser."""

    def test_str(self):
        user = CustomUser.objects.create_user(
            username='ivan', password='secret',
        )
        self.assertEqual(str(user), 'ivan')

    def test_default_values(self):
        user = CustomUser.objects.create_user(username='ivan')
        self.assertEqual(user.purchased_count, 0)
        self.assertEqual(user.phone, '')
        self.assertEqual(user.discount_percent, 0)
        self.assertEqual(user.items_to_max_discount, 50)

    def test_phone_can_be_set(self):
        user = CustomUser.objects.create_user(
            username='ivan', phone='+79001234567',
        )
        self.assertEqual(user.phone, '+79001234567')

    def test_discount_percent_below_limit(self):
        user = CustomUser.objects.create_user(
            username='ivan', purchased_count=10,
        )
        self.assertEqual(user.discount_percent, 10)
        self.assertEqual(user.items_to_max_discount, 40)

    def test_discount_percent_on_limit(self):
        user = CustomUser.objects.create_user(
            username='ivan', purchased_count=50,
        )
        self.assertEqual(user.discount_percent, 50)
        self.assertEqual(user.items_to_max_discount, 0)

    def test_discount_percent_above_limit_is_capped(self):
        user = CustomUser.objects.create_user(
            username='ivan', purchased_count=100,
        )
        self.assertEqual(user.discount_percent, 50)
        self.assertEqual(user.items_to_max_discount, 0)

    def test_items_to_max_discount_never_negative(self):
        user = CustomUser.objects.create_user(
            username='ivan', purchased_count=999,
        )
        self.assertGreaterEqual(user.items_to_max_discount, 0)

    def test_discount_percent_is_int(self):
        user = CustomUser.objects.create_user(
            username='ivan', purchased_count=7,
        )
        self.assertIsInstance(user.discount_percent, int)

    def test_meta_verbose_names(self):
        self.assertEqual(CustomUser._meta.verbose_name, 'Пользователь')
        self.assertEqual(CustomUser._meta.verbose_name_plural, 'Пользователи')


class PurchaseModelTest(TestCase):
    """Тесты модели Purchase."""

    def setUp(self):
        self.user = CustomUser.objects.create_user(username='ivan')
        self.product = Product.objects.create(name='Книга', price=1000)

    def _create_purchase(self, **kwargs):
        defaults = {
            'user': self.user,
            'product': self.product,
            'address': 'ул. Пушкина, 1',
        }
        defaults.update(kwargs)
        return Purchase.objects.create(**defaults)

    def test_str(self):
        purchase = self._create_purchase()
        self.assertEqual(str(purchase), 'ivan — Книга')

    def test_defaults(self):
        purchase = self._create_purchase()
        self.assertEqual(purchase.price, Decimal('0'))
        self.assertEqual(purchase.discount_percent, Decimal('0'))
        self.assertIsNotNone(purchase.date)

    def test_price_and_discount_are_saved(self):
        purchase = self._create_purchase(
            price=Decimal('900.00'),
            discount_percent=Decimal('10.00'),
        )
        purchase.refresh_from_db()
        self.assertEqual(purchase.price, Decimal('900.00'))
        self.assertEqual(purchase.discount_percent, Decimal('10.00'))

    def test_related_name_on_user(self):
        self._create_purchase()
        self._create_purchase()
        self.assertEqual(self.user.purchases.count(), 2)

    def test_default_ordering_by_date_desc(self):
        p1 = self._create_purchase()
        p2 = self._create_purchase()

        # auto_now_add может дать одинаковые метки — выставим вручную
        now = timezone.now()
        Purchase.objects.filter(pk=p1.pk).update(date=now - timezone.timedelta(days=1))
        Purchase.objects.filter(pk=p2.pk).update(date=now)

        ids = list(Purchase.objects.values_list('id', flat=True))
        self.assertEqual(ids, [p2.id, p1.id])

    def test_user_deletion_cascades(self):
        self._create_purchase()
        self.assertEqual(Purchase.objects.count(), 1)
        self.user.delete()
        self.assertEqual(Purchase.objects.count(), 0)

    def test_product_deletion_is_protected(self):
        self._create_purchase()
        with self.assertRaises(ProtectedError):
            self.product.delete()
        self.assertEqual(Purchase.objects.count(), 1)

    def test_meta_verbose_names(self):
        self.assertEqual(Purchase._meta.verbose_name, 'Покупка')
        self.assertEqual(Purchase._meta.verbose_name_plural, 'Покупки')
