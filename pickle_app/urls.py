# pickle_app/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    HomeView, RegisterView, LogoutView, UserProfileView, PasswordChangeView,
    CategoryViewSet, ProductViewSet,
    BatchViewSet, InventoryViewSet,
    OrderViewSet, PaymentViewSet,
    CreatePaymentIntentView, ConfirmPaymentView,
    SearchView
)

router = DefaultRouter()
router.register(r'products/categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'inventory/batches', BatchViewSet, basename='batch')
router.register(r'inventory', InventoryViewSet, basename='inventory')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    # Authentication endpoints
    path('', HomeView.as_view(), name='home'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/profile/', UserProfileView.as_view(), name='user_profile'),
    path('auth/password/change/', PasswordChangeView.as_view(), name='password_change'),
    
    # Payment processing endpoints
    path('payments/create-payment-intent/', CreatePaymentIntentView.as_view(), name='create_payment_intent'),
    path('payments/confirm-payment/', ConfirmPaymentView.as_view(), name='confirm_payment'),
    
    # Search endpoint
    path('search/', SearchView.as_view(), name='search'),
    
    # Router endpoints
    path('', include(router.urls)),
]