from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from shop.models import CustomUser, Product, Purchase
from shop.services import apply_discount


class IndexViewTests(TestCase):
    def test_empty_catalog(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Товаров пока нет')
        self.assertContains(response, 'Войти')
        self.assertNotContains(response, 'Профиль')

    def test_anonymous_sees_full_prices(self):
        Product.objects.create(name='Книга', price=1000)
        response = self.client.get(reverse('index'))
        self.assertContains(response, 'Книга')
        self.assertContains(response, '1000 ₽')
        self.assertNotContains(response, 'персональная скидка')
        self.assertEqual(response.context['discount'], Decimal('0'))

    def test_buyer_sees_discounted_price(self):
        user = CustomUser.objects.create_user(
            username='ivan', password='Str0ng-pass-99', purchased_count=10,
        )
        product = Product.objects.create(name='Книга', price=999)
        self.client.force_login(user)

        response = self.client.get(reverse('index'))
        self.assertContains(response, 'персональная скидка')
        self.assertContains(response, '10%')
        self.assertContains(response, '999')
        self.assertContains(response, '899.10')
        row = next(p for p in response.context['products'] if p.pk == product.pk)
        self.assertEqual(row.price_old, 999)
        self.assertEqual(row.price_final, apply_discount(999, 10))
        self.assertContains(response, 'Привет')
        self.assertContains(response, 'ivan')


class AuthViewTests(TestCase):
    def test_register_page_renders(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Регистрация')
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_register_logs_user_in_and_opens_profile(self):
        response = self.client.post(reverse('register'), {
            'username': 'ivan',
            'email': 'ivan@example.com',
            'phone': '+79001112233',
            'password1': 'Str0ng-pass-99',
            'password2': 'Str0ng-pass-99',
        })
        self.assertRedirects(response, reverse('profile'))
        user = CustomUser.objects.get(username='ivan')
        self.assertEqual(user.email, 'ivan@example.com')
        self.assertEqual(user.phone, '+79001112233')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

        profile = self.client.get(reverse('profile'))
        self.assertContains(profile, 'ivan@example.com')
        self.assertContains(profile, '+79001112233')
        self.assertContains(profile, 'Покупок пока нет')

    def test_register_rejects_invalid_data(self):
        response = self.client.post(reverse('register'), {
            'username': 'ivan',
            'email': '',
            'phone': '',
            'password1': 'Str0ng-pass-99',
            'password2': 'different-pass',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(CustomUser.objects.filter(username='ivan').exists())
        self.assertContains(response, 'Регистрация')

    def test_login_page_renders(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Вход')

    def test_login_redirects_to_profile(self):
        CustomUser.objects.create_user(username='ivan', password='Str0ng-pass-99')
        response = self.client.post(reverse('login'), {
            'username': 'ivan',
            'password': 'Str0ng-pass-99',
        })
        self.assertRedirects(response, reverse('profile'))

    def test_login_rejects_wrong_password(self):
        CustomUser.objects.create_user(username='ivan', password='Str0ng-pass-99')
        response = self.client.post(reverse('login'), {
            'username': 'ivan',
            'password': 'wrong-password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout_post_ends_session(self):
        user = CustomUser.objects.create_user(username='ivan', password='Str0ng-pass-99')
        self.client.force_login(user)
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout_get_also_ends_session(self):
        user = CustomUser.objects.create_user(username='ivan', password='Str0ng-pass-99')
        self.client.force_login(user)
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_profile_requires_login(self):
        response = self.client.get(reverse('profile'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('profile')}")


class PurchaseViewTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='ivan',
            password='Str0ng-pass-99',
            purchased_count=10,
        )
        self.other = CustomUser.objects.create_user(
            username='olga',
            password='Str0ng-pass-99',
        )
        self.product = Product.objects.create(name='Книга', price=1000)
        self.url = reverse('buy', args=[self.product.pk])

    def test_anonymous_is_redirected_to_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_get_shows_form_for_buyer(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Оформление покупки')
        self.assertContains(response, 'ivan')
        self.assertContains(response, 'Адрес доставки')

    def test_post_saves_discounted_price_and_increments_counter(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {'address': 'ул. Ленина, 1'})
        self.assertRedirects(response, reverse('index'))

        purchase = Purchase.objects.get()
        self.assertEqual(purchase.user, self.user)
        self.assertEqual(purchase.product, self.product)
        self.assertEqual(purchase.address, 'ул. Ленина, 1')
        self.assertEqual(purchase.price, Decimal('900.00'))
        self.assertEqual(purchase.discount_percent, Decimal('10.00'))

        self.user.refresh_from_db()
        self.assertEqual(self.user.purchased_count, 11)

    def test_next_purchase_uses_updated_discount_and_keeps_old_snapshot(self):
        self.user.purchased_count = 49
        self.user.save(update_fields=['purchased_count'])
        self.client.force_login(self.user)
        product = Product.objects.create(name='Лампа', price=200)
        url = reverse('buy', args=[product.pk])

        self.client.post(url, {'address': 'адрес 1'})
        self.client.post(url, {'address': 'адрес 2'})

        first, second = Purchase.objects.filter(product=product).order_by('date', 'id')
        self.assertEqual(first.price, Decimal('102.00'))
        self.assertEqual(first.discount_percent, Decimal('49.00'))
        self.assertEqual(second.price, Decimal('100.00'))
        self.assertEqual(second.discount_percent, Decimal('50.00'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.purchased_count, 51)
        self.assertEqual(self.user.discount_percent, 50)

    def test_htmx_returns_success_fragment(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
            {'address': 'ул. Ленина, 1'},
            headers={'HX-Request': 'true'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Покупка оформлена')
        self.assertContains(response, 'Книга')
        self.assertContains(response, 'ул. Ленина, 1')
        self.assertContains(response, '900.00')
        self.assertNotContains(response, 'Каталог')
        self.assertEqual(Purchase.objects.count(), 1)

    def test_blank_address_does_not_create_purchase(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {'address': '   '})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Purchase.objects.count(), 0)
        self.user.refresh_from_db()
        self.assertEqual(self.user.purchased_count, 10)

    def test_missing_product_returns_404(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('buy', args=[99999]), {'address': 'дом 1'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Purchase.objects.count(), 0)

    def test_profile_lists_only_own_purchases(self):
        Purchase.objects.create(
            user=self.user,
            product=self.product,
            address='мой адрес',
            price=Decimal('900.00'),
            discount_percent=Decimal('10.00'),
        )
        Purchase.objects.create(
            user=self.other,
            product=self.product,
            address='чужой адрес',
            price=Decimal('1000.00'),
            discount_percent=Decimal('0.00'),
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Книга')
        self.assertContains(response, 'мой адрес')
        self.assertContains(response, '900.00')
        self.assertContains(response, '10.00%')
        self.assertNotContains(response, 'чужой адрес')
        self.assertEqual(list(response.context['purchases']), list(self.user.purchases.all()))
