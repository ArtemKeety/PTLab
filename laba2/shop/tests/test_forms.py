from django.test import TestCase

from shop.forms import LoginForm, RegisterForm
from shop.models import CustomUser


class RegisterFormTests(TestCase):
    def _data(self, **overrides):
        data = {
            'username': 'ivan',
            'email': 'ivan@example.com',
            'phone': '+79001234567',
            'password1': 'Str0ng-pass-99',
            'password2': 'Str0ng-pass-99',
        }
        data.update(overrides)
        return data

    def test_valid_form_creates_user_with_email_and_phone(self):
        form = RegisterForm(data=self._data())
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.username, 'ivan')
        self.assertEqual(user.email, 'ivan@example.com')
        self.assertEqual(user.phone, '+79001234567')
        self.assertEqual(user.purchased_count, 0)
        self.assertTrue(user.check_password('Str0ng-pass-99'))

    def test_phone_is_optional(self):
        form = RegisterForm(data=self._data(phone=''))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().phone, '')

    def test_email_is_required(self):
        form = RegisterForm(data=self._data(email=''))
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_password_mismatch(self):
        form = RegisterForm(data=self._data(password2='other-password'))
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_short_password_is_rejected(self):
        form = RegisterForm(data=self._data(password1='short', password2='short'))
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_duplicate_username_is_rejected(self):
        CustomUser.objects.create_user(username='ivan', password='Str0ng-pass-99')
        form = RegisterForm(data=self._data())
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_labels(self):
        form = RegisterForm()
        self.assertEqual(form.fields['email'].label, 'Email')
        self.assertEqual(form.fields['phone'].label, 'Телефон')


class LoginFormTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='ivan',
            password='Str0ng-pass-99',
        )

    def test_labels(self):
        form = LoginForm()
        self.assertEqual(form.fields['username'].label, 'Логин')
        self.assertEqual(form.fields['password'].label, 'Пароль')

    def test_valid_credentials(self):
        form = LoginForm(data={'username': 'ivan', 'password': 'Str0ng-pass-99'})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.get_user(), self.user)

    def test_wrong_password(self):
        form = LoginForm(data={'username': 'ivan', 'password': 'wrong-password'})
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)

    def test_unknown_user(self):
        form = LoginForm(data={'username': 'nobody', 'password': 'Str0ng-pass-99'})
        self.assertFalse(form.is_valid())
