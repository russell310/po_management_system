from rest_framework import serializers
from .models import PurchaseOrder, PurchaseOrderItem, InventoryTransaction
from ..product.models import Product


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    class Meta:
        model = PurchaseOrderItem
        fields = ['id', 'product', 'product_name', 'ordered_quantity', 'received_quantity']
        read_only_fields = ['received_quantity']


class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemSerializer(many=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = ['id', 'supplier', 'supplier_name', 'created_by', 'created_by_name', 'status', 'created_at', 'items']
        read_only_fields = ['status']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        po = PurchaseOrder.objects.create(**validated_data)
        for item in items_data:
            PurchaseOrderItem.objects.create(po=po, **item)
        return po


class PurchaseOrderReceiveItemSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    received_quantity = serializers.IntegerField(min_value=1)

class PurchaseOrderReceiveSerializer(serializers.Serializer):
    items = PurchaseOrderReceiveItemSerializer(many=True)

    def validate(self, data):
        if not data['items']:
            raise serializers.ValidationError("At least one item must be provided.")

        po = self.context.get('po')
        po_items = {item.product.id: item for item in po.items.all()}

        for entry in data['items']:
            product = entry['product']
            received_quantity = entry['received_quantity']

            # check product id is in po/not
            if product.id not in po_items:
                raise serializers.ValidationError(f"Product {product.name} is not part of this PO.")

            po_item = po_items[product.id]
            # check total receive quantity
            if po_item.received_quantity + received_quantity > po_item.ordered_quantity:
                raise serializers.ValidationError(
                    f"Received quantity for {product.id} exceeds the ordered quantity."
                )

        return data