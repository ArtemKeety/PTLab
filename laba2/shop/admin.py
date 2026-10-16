from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Product, Purchase


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone', 'purchased_count', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'phone')
    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {
            'fields': ('phone', 'purchased_count'),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительно', {
            'fields': ('email', 'phone'),
        }),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price')
    search_fields = ('name',)
    ordering = ('id',)


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'product',
        'price', 'discount_percent',
        'address', 'date',
    )
    list_filter = ('user', 'product', 'discount_percent', 'date')
    search_fields = ('user__username', 'product__name', 'address')
    date_hierarchy = 'date'
    autocomplete_fields = ('user', 'product')
    readonly_fields = ('price', 'discount_percent', 'date')
    ordering = ('-date',)
