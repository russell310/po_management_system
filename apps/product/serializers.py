from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'sku', 'stock_quantity', 'reorder_threshold', 'reorder_needed']
        read_only_fields = ['reorder_needed']