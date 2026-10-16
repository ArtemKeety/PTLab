from django.db import models
from django.contrib.auth.models import AbstractUser


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    def price_with_discount(self, discount_percent) -> float:
        return self.price - self.price * discount_percent // 100


class CustomUser(AbstractUser):
    """Расширенная модель пользователя."""

    phone = models.CharField('Телефон', max_length=20, blank=True)
    purchased_count = models.PositiveIntegerField('Куплено товаров', default=0)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def discount_percent(self):
        return min(self.purchased_count, 50)

    @property
    def items_to_max_discount(self):
        return max(0, 50 - self.purchased_count)


class Purchase(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='purchases',
        verbose_name='Покупатель',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name='Товар',
    )
    address = models.CharField('Адрес', max_length=200)

    price = models.DecimalField(
        'Цена со скидкой', max_digits=10, decimal_places=2, default=0,
    )
    discount_percent = models.DecimalField(
        'Скидка, %', max_digits=5, decimal_places=2, default=0,
    )

    date = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
        ordering = ['-date']

    def __str__(self):
        return f'{self.user.username} — {self.product.name}'
