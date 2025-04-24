from django.shortcuts import render
from rest_framework import viewsets
from .models import Supplier
from .serializers import SupplierSerializer


# Create your views here.

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all().order_by('id')
    serializer_class = SupplierSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)