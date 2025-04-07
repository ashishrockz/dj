# accounts/admin.py
from django.contrib import admin
from .models import User, Product, Order

# Custom admin for User
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'user_type', 'is_active', 'date_joined')
    list_filter = ('user_type', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)

# Custom admin for Product
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'created_at')
    list_filter = ('created_at', 'price')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)

# Custom admin for Order
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'product', 'quantity', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('client__username', 'product__name')
    ordering = ('-created_at',)

# Register the models with their custom admin classes
admin.site.register(User, UserAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)