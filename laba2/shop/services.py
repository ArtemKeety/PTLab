from decimal import Decimal, ROUND_HALF_UP


def apply_discount(price, discount_percent):
    discount = Decimal(str(discount_percent or 0))
    coef = (Decimal(100) - discount) / Decimal(100)
    return (Decimal(str(price)) * coef).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)