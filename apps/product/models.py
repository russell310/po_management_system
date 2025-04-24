from django.db import models
from ..helpers.models import TimeStamp


# Create your models here.

class Product(TimeStamp):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    stock_quantity = models.IntegerField(default=0)
    reorder_threshold = models.IntegerField(default=10)
    reorder_needed = models.BooleanField(default=False)