from decimal import Decimal
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import F
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView

from .forms import RegisterForm, LoginForm
from .models import Product, Purchase, CustomUser
from .services import apply_discount


def index(request):
    products = Product.objects.all()
    discount = request.user.discount_percent if request.user.is_authenticated else 0
    discount = Decimal(str(discount or 0))

    for p in products:
        p.price_old = p.price
        p.price_final = apply_discount(p.price, discount)

    return render(request, 'shop/index.html', {
        'products': products,
        'discount': discount,
    })


@method_decorator(login_required, name='dispatch')
class PurchaseCreate(CreateView):
    model = Purchase
    fields = ['address']
    template_name = 'shop/purchase_form.html'

    def form_valid(self, form):
        product = get_object_or_404(Product, pk=self.kwargs['product_id'])
        user = self.request.user

        # --- считаем цену со скидкой ---
        discount = Decimal(str(user.discount_percent or 0))
        final_price = apply_discount(product.price, discount)

        # --- записываем снимок в Purchase ---
        form.instance.user = user
        form.instance.product = product
        form.instance.price = final_price
        form.instance.discount_percent = discount
        self.object = form.save()

        CustomUser.objects.filter(pk=user.pk).update(
            purchased_count=F('purchased_count') + 1
        )

        if self.request.headers.get('HX-Request'):
            return render(self.request, 'shop/_purchase_success.html', {
                'product': product,
                'address': self.object.address,
                'price': final_price,
                'discount': discount,
            })

        return redirect('index')


# ---------- Авторизация ----------

class RegisterView(CreateView):
    model = CustomUser
    form_class = RegisterForm
    template_name = 'shop/register.html'
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'shop/login.html'


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    return render(request, 'shop/profile.html', {
        'user': request.user,
        'purchases': request.user.purchases.select_related('product'),
    })
