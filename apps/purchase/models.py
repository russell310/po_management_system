from django.db import models
from ..helpers.models import TimeStamp
from ..product.models import Product
from ..supplier.models import Supplier


# Create your models here.

class PurchaseOrder(TimeStamp):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('partially_delivered', 'Partially Delivered'),
        ('completed', 'Completed'),
    ]
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

class PurchaseOrderItem(models.Model):
    po = models.ForeignKey(PurchaseOrder, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ordered_quantity = models.PositiveIntegerField()
    received_quantity = models.PositiveIntegerField(default=0)

class InventoryTransaction(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    transaction_type = models.CharField(max_length=50)
    po = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)