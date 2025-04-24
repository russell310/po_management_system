from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from rest_framework_simplejwt.tokens import RefreshToken

from supplier.models import Supplier
from product.models import Product
from purchase.models import PurchaseOrder, PurchaseOrderItem


class PurchaseOrderTests(TestCase):

    def setUp(self):
        self.client = Client()

        # Create "Manager" group if it doesn't exist
        manager_group, _ = Group.objects.get_or_create(name="Manager")

        # Create user and add to "Manager" group
        self.manager = User.objects.create_user(username='manager', password='testpass', is_staff=True)
        self.manager.groups.add(manager_group)

        # 🔥 Force reload of user to reflect group assignment
        self.manager = User.objects.get(pk=self.manager.pk)

        # Create JWT token for the manager
        refresh = RefreshToken.for_user(self.manager)
        self.access_token = str(refresh.access_token)

        # Add token to default client headers
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {self.access_token}'

        # Set up supplier and product
        self.supplier = Supplier.objects.create(name="Test Supplier")
        self.product = Product.objects.create(name="Test Product", stock_quantity=10, reorder_threshold=5)

        self.po_data = {
            "supplier": self.supplier.id,
            "items": [{
                "product": self.product.id,
                "ordered_quantity": 5
            }]
        }

    def test_create_purchase_order(self):
        url = reverse('purchaseorder-list')
        response = self.client.post(url, data=self.po_data, content_type='application/json')
        print("Create PO Response:", response.status_code, response.json())
        self.assertEqual(response.status_code, 201)
        self.assertEqual(PurchaseOrder.objects.count(), 1)
        self.assertEqual(PurchaseOrderItem.objects.count(), 1)

    def test_approve_purchase_order(self):
        # Create PO
        create_response = self.client.post(reverse('purchaseorder-list'), data=self.po_data, content_type='application/json')
        po_id = create_response.json().get('id')
        self.assertIsNotNone(po_id, "Purchase Order creation failed; no ID returned.")

        # Approve PO
        response = self.client.post(reverse('purchaseorder-approve', args=[po_id]))
        print("Approve Response:", response.status_code, response.json())
        self.assertEqual(response.status_code, 200)

        po = PurchaseOrder.objects.get(id=po_id)
        self.assertEqual(po.status, 'approved')

    def test_receive_items(self):
        # Create and approve PO
        create_response = self.client.post(reverse('purchaseorder-list'), data=self.po_data, content_type='application/json')
        po_id = create_response.json().get('id')
        self.assertIsNotNone(po_id, "Purchase Order creation failed; no ID returned.")

        self.client.post(reverse('purchaseorder-approve', args=[po_id]))

        # Receive part of the items
        receive_data = {
            "items": [{
                "product": self.product.id,
                "received_quantity": 3
            }]
        }
        response = self.client.post(reverse('purchaseorder-receive', args=[po_id]), data=receive_data, content_type='application/json')
        self.assertEqual(response.status_code, 200)

        po = PurchaseOrder.objects.get(id=po_id)
        self.assertEqual(po.status, 'partially_delivered')
        item = po.items.get(product=self.product)
        self.assertEqual(item.received_quantity, 3)

        # Receive remaining items
        receive_data["items"][0]["received_quantity"] = 2
        response = self.client.post(reverse('purchaseorder-receive', args=[po_id]), data=receive_data, content_type='application/json')
        self.assertEqual(response.status_code, 200)

        po.refresh_from_db()
        item.refresh_from_db()
        self.assertEqual(po.status, 'completed')
        self.assertEqual(item.received_quantity, 5)

    def test_only_pending_po_can_be_deleted(self):
        # Create PO
        create_response = self.client.post(reverse('purchaseorder-list'), data=self.po_data, content_type='application/json')
        po_id = create_response.json().get('id')
        self.assertIsNotNone(po_id, "Purchase Order creation failed; no ID returned.")
        po = PurchaseOrder.objects.get(id=po_id)

        # Try deleting when status is approved
        po.status = 'approved'
        po.save()
        response = self.client.delete(reverse('purchaseorder-detail', args=[po_id]))
        self.assertEqual(response.status_code, 400)

        # Try deleting when status is pending
        po.status = 'pending'
        po.save()
        response = self.client.delete(reverse('purchaseorder-detail', args=[po_id]))
        self.assertEqual(response.status_code, 204)
