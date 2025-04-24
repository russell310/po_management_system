from django.db import models
from ..helpers.models import TimeStamp


# Create your models here.

class Supplier(TimeStamp):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)