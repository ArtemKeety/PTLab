from django.test import SimpleTestCase
from django.urls import resolve, reverse

from shop import views


class ShopUrlTests(SimpleTestCase):
    def test_index(self):
        self.assertEqual(reverse('index'), '/')
        self.assertIs(resolve('/').func, views.index)

    def test_buy(self):
        self.assertEqual(reverse('buy', args=[5]), '/buy/5/')
        match = resolve('/buy/5/')
        self.assertIs(match.func.view_class, views.PurchaseCreate)
        self.assertEqual(match.kwargs['product_id'], 5)

    def test_register(self):
        self.assertEqual(reverse('register'), '/register/')
        self.assertIs(resolve('/register/').func.view_class, views.RegisterView)

    def test_login(self):
        self.assertEqual(reverse('login'), '/login/')
        self.assertIs(resolve('/login/').func.view_class, views.CustomLoginView)

    def test_logout(self):
        self.assertEqual(reverse('logout'), '/logout/')
        self.assertIs(resolve('/logout/').func, views.logout_view)

    def test_profile(self):
        self.assertEqual(reverse('profile'), '/profile/')
        self.assertIs(resolve('/profile/').func, views.profile_view)

    def test_admin_is_mounted(self):
        self.assertEqual(reverse('admin:index'), '/admin/')
