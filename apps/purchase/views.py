from django.shortcuts import render
from django.views.generic import ListView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import PurchaseOrder, InventoryTransaction
from .serializers import PurchaseOrderSerializer, PurchaseOrderReceiveSerializer
from django.db import transaction

from ..helpers.permissions import IsManager


# Create your views here.


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """
        ViewSet for managing Purchase Orders.

        Provides standard CRUD operations with additional custom actions for approving and receiving POs.
        Integrates filtering and permission control.

        Methods:
            perform_create(serializer):
                Automatically sets 'created_by' to the current user on PO creation.

            approve(request, pk=None):
                Custom action to approve a pending Purchase Order.
                Only users in the "Manager" group can perform this action.
                Returns 400 if the PO is not in 'pending' status.

            receive(request, pk=None):
                Custom action to receive items against an approved or partially delivered PO.
                Validates quantities, updates stock, and logs inventory transactions.
                Automatically updates the PO status to 'completed' or 'partially_delivered'.

            destroy(request, *args, **kwargs):
                Prevents deletion of POs unless they are in 'pending' status.
                Returns 400 if trying to delete a PO that has already been approved or processed.
        """
    queryset = PurchaseOrder.objects.all().order_by('id').prefetch_related('items')
    serializer_class = PurchaseOrderSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status',]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsManager])
    def approve(self, request, pk=None):
        po = self.get_object()
        if po.status != 'pending':
            return Response({"detail": "Only pending POs can be approved."}, status=400)
        po.status = 'approved'
        po.save()
        return Response(self.get_serializer(po).data)

    @action(detail=True, methods=['post'])
    def receive(self, request, pk=None):
        po = self.get_object()

        if po.status not in ['approved', 'partially_delivered']:
            return Response({"detail": "PO must be approved or partially delivered to receive items."}, status=400)

        serializer = PurchaseOrderReceiveSerializer(data=request.data, context={'po': po})
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        with transaction.atomic():
            all_received = True
            for entry in validated_data['items']:
                product = entry['product']
                received_qty = entry['received_quantity']

                po_item = po.items.get(product=product)
                po_item.received_quantity += received_qty
                po_item.save()

                product.stock_quantity += received_qty
                product.reorder_needed = product.stock_quantity < product.reorder_threshold
                product.save()

                # save transaction for each entry
                InventoryTransaction.objects.create(
                    product=product,
                    quantity=received_qty,
                    transaction_type="RECEIVED_PO",
                    po=po
                )

                if po_item.received_quantity < po_item.ordered_quantity:
                    all_received = False

            po.status = 'completed' if all_received else 'partially_delivered'
            po.save()

        return Response(self.get_serializer(po).data)

    def destroy(self, request, *args, **kwargs):
        po = self.get_object()
        if po.status != 'pending':
            return Response({"detail": "Only pending POs can be deleted."}, status=400)
        return super().destroy(request, *args, **kwargs)


class PurchaseOrderListView(ListView):
    template_name = 'dashboard.html'
    model = PurchaseOrder
    context_object_name = 'pending_pos'

    def get_queryset(self):
        return PurchaseOrder.objects.exclude(status='completed')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['completed_pos'] = PurchaseOrder.objects.filter(status='completed')
        return context