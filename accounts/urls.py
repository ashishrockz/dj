# accounts/urls.py
from django.urls import path
from .views import (
    RegisterView, LoginView, ProfileView,
    ProductListCreateView, ProductDetailView,
    OrderListCreateView, OrderDetailView
)

urlpatterns = [
    path('', RegisterView.as_view(), name='home'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('products/', ProductListCreateView.as_view(), name='product_list_create'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('orders/', OrderListCreateView.as_view(), name='order_list_create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
]