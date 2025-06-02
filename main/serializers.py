from rest_framework import serializers
from .models import ProductCategory, Product, CartItem

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'description', 'created_at']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'category_name', 
                 'stock', 'sales_count', 'is_active', 'created_at', 'image']

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'total_price', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("数量必须大于0")
        return value

    def validate(self, data):
        product = data['product']
        quantity = data['quantity']
        
        if not product.is_active:
            raise serializers.ValidationError("该商品已下架")
        
        if quantity > product.stock:
            raise serializers.ValidationError("商品库存不足")
        
        return data 