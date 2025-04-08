# pickle_app/views.py
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q, F
from rest_framework import viewsets, generics, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Category, Product, ProductImage, ProductVariant,
    Batch, InventoryItem, Order, OrderItem, Payment
)
from .serializers import (
    UserSerializer, RegisterSerializer, PasswordChangeSerializer,
    CategorySerializer, ProductSerializer, ProductImageSerializer, ProductVariantSerializer,
    BatchSerializer, InventoryItemSerializer,
    OrderSerializer, OrderCreateSerializer, OrderItemSerializer,
    PaymentSerializer, PaymentIntentSerializer, PaymentConfirmSerializer
)
from .permissions import IsAdminUser, IsStaffUser, IsOwnerOrAdmin

User = get_user_model()
class HomeView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    
    def get(self, request):
        return Response({
            "message": "Welcome to Pickle Paradise!",
            "tagline": "Savor the taste of tradition with every bite.",
            "info": "Browse our products, place an order, or sign up to join our foodie community!"
        }, status=status.HTTP_200_OK)
# Authentication Views
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer
     

class LogoutView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

class PasswordChangeView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PasswordChangeSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['current_password']):
                return Response({"current_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Category Views
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsStaffUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

# Product Views
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'available', 'featured']
    search_fields = ['name', 'description', 'ingredients']
    ordering_fields = ['name', 'price', 'created_at']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'add_image', 'add_variant']:
            permission_classes = [IsStaffUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def add_image(self, request, slug=None):
        product = self.get_object()
        serializer = ProductImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def add_variant(self, request, slug=None):
        product = self.get_object()
        serializer = ProductVariantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Inventory Views
class BatchViewSet(viewsets.ModelViewSet):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer
    permission_classes = [IsStaffUser]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['production_date', 'expiry_date', 'created_at']

class InventoryViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    permission_classes = [IsStaffUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['product_variant', 'batch']
    ordering_fields = ['quantity', 'created_at', 'updated_at']

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        low_stock_items = InventoryItem.objects.filter(
            quantity__lte=F('low_stock_threshold')
        )
        serializer = self.get_serializer(low_stock_items, many=True)
        return Response(serializer.data)

# Order Views
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at', 'total']

    def get_queryset(self):
        if self.request.user.role in ['ADMIN', 'STAFF']:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy', 'update_status']:
            permission_classes = [IsStaffUser]
        elif self.action == 'list':
            permission_classes = [IsAuthenticated]  # Completed the incomplete line
        else:
            permission_classes = [IsOwnerOrAdmin]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        
        # Update inventory after order creation
        for item in order.items.all():
            # Find inventory items for this product variant
            inventory_items = InventoryItem.objects.filter(product_variant=item.product_variant)
            
            quantity_to_fulfill = item.quantity
            for inv_item in inventory_items.order_by('batch__expiry_date'):  # FIFO inventory management
                if quantity_to_fulfill <= 0:
                    break
                
                if inv_item.quantity >= quantity_to_fulfill:
                    inv_item.quantity -= quantity_to_fulfill
                    inv_item.save()
                    quantity_to_fulfill = 0
                else:
                    quantity_to_fulfill -= inv_item.quantity
                    inv_item.quantity = 0
                    inv_item.save()
            
            # Check if we couldn't fulfill the order
            if quantity_to_fulfill > 0:
                # Handle stockout situation
                # You might want to flag this order for review
                order.notes = f"{order.notes}\nWARNING: Insufficient stock for {item.product_variant}."
                order.save()
        
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        
        # Only pending or processing orders can be cancelled
        if order.status not in ['PENDING', 'PROCESSING']:
            return Response(
                {"detail": "Only pending or processing orders can be cancelled."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user has permission (either admin/staff or the order owner)
        if not (request.user.role in ['ADMIN', 'STAFF'] or order.user == request.user):
            return Response(
                {"detail": "You don't have permission to cancel this order."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        order.status = 'CANCELLED'
        order.save()
        
        # Return inventory items to stock
        for item in order.items.all():
            # Create or update inventory item
            inventory, created = InventoryItem.objects.get_or_create(
                product_variant=item.product_variant,
                batch=Batch.objects.latest('created_at'),  # This is simplified; you might want to track which batch was used
                defaults={'quantity': item.quantity}
            )
            
            if not created:
                inventory.quantity += item.quantity
                inventory.save()
        
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        status_value = request.data.get('status')
        
        if not status_value:
            return Response(
                {"detail": "Status is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate status value
        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        if status_value not in valid_statuses:
            return Response(
                {"detail": f"Invalid status. Must be one of {valid_statuses}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = status_value
        order.save()
        
        return Response(OrderSerializer(order).data)

# Payment Views
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsStaffUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['order', 'status', 'payment_method']
    ordering_fields = ['created_at', 'amount']

class CreatePaymentIntentView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentIntentSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        order_id = serializer.validated_data['order_id']
        amount = serializer.validated_data['amount']
        
        # Get the order and verify the user has access
        order = get_object_or_404(Order, id=order_id)
        if not (request.user.role in ['ADMIN', 'STAFF'] or order.user == request.user):
            return Response(
                {"detail": "You don't have permission to create a payment for this order."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Here you would integrate with a payment processor like Stripe
        # This is a simplified example - in a real app, you'd call Stripe's API
        # to create a payment intent and return the client secret
        
        # For this example, we'll simulate a successful payment intent creation
        client_secret = f"pi_simulated_{order_id}_{amount}_secret"
        
        return Response({"clientSecret": client_secret})

class ConfirmPaymentView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentConfirmSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        order_id = serializer.validated_data['order_id']
        payment_intent_id = serializer.validated_data['payment_intent_id']
        payment_method = serializer.validated_data['payment_method']
        
        # Get the order and verify it exists
        order = get_object_or_404(Order, id=order_id)
        
        # Here you would verify the payment with your payment processor
        # For this example, we'll simulate a successful payment
        
        # Create the payment record
        payment = Payment.objects.create(
            order=order,
            amount=order.total,
            payment_method=payment_method,
            transaction_id=payment_intent_id,
            status='COMPLETED'
        )
        
        # Update the order status
        order.status = 'PROCESSING'
        order.save()
        
        return Response({
            "success": True,
            "payment": PaymentSerializer(payment).data
        })

# Search View
class SearchView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['name', 'description', 'ingredients', 'category__name']
    filterset_fields = ['category__slug']
    ordering_fields = ['name', 'price', 'created_at']
    
    def get_queryset(self):
        queryset = Product.objects.filter(available=True)
        
        # Additional filtering
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
            
        # Handle custom sort_by parameter
        sort_by = self.request.query_params.get('sort_by')
        if sort_by:
            if sort_by == 'price_asc':
                queryset = queryset.order_by('price')
            elif sort_by == 'price_desc':
                queryset = queryset.order_by('-price')
            elif sort_by == 'newest':
                queryset = queryset.order_by('-created_at')
            elif sort_by == 'name':
                queryset = queryset.order_by('name')
        
        return queryset  # Ensure the return statement is complete