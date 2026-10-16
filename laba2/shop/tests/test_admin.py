from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.test import TestCase
from django.urls import reverse

from shop.admin import CustomUserAdmin, ProductAdmin, PurchaseAdmin
from shop.models import CustomUser, Product, Purchase


class AdminRegistrationTests(TestCase):
    def test_models_are_registered_with_expected_admins(self):
        registry = admin.site._registry
        self.assertIsInstance(registry[CustomUser], CustomUserAdmin)
        self.assertIsInstance(registry[Product], ProductAdmin)
        self.assertIsInstance(registry[Purchase], PurchaseAdmin)

    def test_user_admin_extends_user_admin_and_shows_shop_fields(self):
        self.assertTrue(issubclass(CustomUserAdmin, UserAdmin))
        self.assertIn('phone', CustomUserAdmin.list_display)
        self.assertIn('purchased_count', CustomUserAdmin.list_display)
        self.assertIn('phone', CustomUserAdmin.search_fields)
        extra_fields = CustomUserAdmin.fieldsets[-1][1]['fields']
        self.assertEqual(extra_fields, ('phone', 'purchased_count'))

    def test_product_admin_is_searchable(self):
        self.assertEqual(ProductAdmin.list_display, ('id', 'name', 'price'))
        self.assertEqual(ProductAdmin.search_fields, ('name',))

    def test_purchase_snapshot_fields_are_readonly(self):
        self.assertIn('price', PurchaseAdmin.readonly_fields)
        self.assertIn('discount_percent', PurchaseAdmin.readonly_fields)
        self.assertIn('date', PurchaseAdmin.readonly_fields)
        self.assertEqual(PurchaseAdmin.autocomplete_fields, ('user', 'product'))


class AdminAccessTests(TestCase):
    def setUp(self):
        self.staff = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='Str0ng-pass-99',
        )
        self.customer = CustomUser.objects.create_user(
            username='ivan',
            password='Str0ng-pass-99',
        )
        self.product = Product.objects.create(name='Книга', price=1000)
        self.purchase = Purchase.objects.create(
            user=self.customer,
            product=self.product,
            address='ул. Пушкина, 1',
            price='1000.00',
            discount_percent='0.00',
        )

    def test_anonymous_is_redirected_from_admin(self):
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)

    def test_customer_cannot_open_admin(self):
        self.client.force_login(self.customer)
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)

    def test_staff_can_open_changelists(self):
        self.client.force_login(self.staff)
        for url in (
            reverse('admin:index'),
            reverse('admin:shop_customuser_changelist'),
            reverse('admin:shop_product_changelist'),
            reverse('admin:shop_purchase_changelist'),
            reverse('admin:shop_product_change', args=[self.product.pk]),
            reverse('admin:shop_purchase_change', args=[self.purchase.pk]),
        ):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
