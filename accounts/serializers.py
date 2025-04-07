# accounts/serializers.py
from rest_framework import serializers
from .models import User, Product, Order

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'user_type')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            user_type=validated_data['user_type']
        )
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'stock', 'image', 'created_at')  # Added image

class OrderSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(user_type='client'))
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product', write_only=True)

    class Meta:
        model = Order
        fields = ('id', 'client', 'product', 'product_id', 'quantity', 'total_price', 'status', 'delivery_address', 'created_at')