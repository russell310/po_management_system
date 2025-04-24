from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from faker import Faker
import random

from apps.product.models import Product
from apps.supplier.models import Supplier


class Command(BaseCommand):
    help = 'Seed database with suppliers, products, and preset users/groups.'

    def add_arguments(self, parser):
        parser.add_argument('--suppliers', type=int, default=10)
        parser.add_argument('--products', type=int, default=50)

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Create Groups
        manager_group, _ = Group.objects.get_or_create(name="Manager")
        employee_group, _ = Group.objects.get_or_create(name="Employee")

        # Preset Users
        preset_users = [
            ("manager1", "manager1@example.com", "admin123", manager_group),
            ("manager2", "manager2@example.com", "admin123", manager_group),
            ("employee1", "employee1@example.com", "admin123", employee_group),
            ("employee2", "employee2@example.com", "admin123", employee_group),
        ]

        self.stdout.write("Creating preset users...")
        for username, email, password, group in preset_users:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, email=email, password=password)
                user.groups.add(group)
                self.stdout.write(f"Created {username} in group {group.name} with password '{password}'")
            else:
                self.stdout.write(f"{username} already exists — skipping.")

        # Superuser: demo/demo
        if not User.objects.filter(username="demo").exists():
            User.objects.create_superuser("demo", "demo@example.com", "demo")
            self.stdout.write("Created superuser: demo / demo")
        else:
            self.stdout.write("Superuser 'demo' already exists — skipping.")

        # Suppliers
        suppliers_count = kwargs['suppliers']
        suppliers = [
            Supplier(
                name=fake.company(),
                email=fake.company_email(),
                phone=fake.phone_number()
            )
            for _ in range(suppliers_count)
        ]
        Supplier.objects.bulk_create(suppliers)

        # Products
        products_count = kwargs['products']
        products = [
            Product(
                name=fake.word().capitalize() + " " + fake.word().capitalize(),
                sku=fake.unique.bothify(text='???-#####'),
                stock_quantity=random.randint(0, 100),
                reorder_threshold=random.randint(5, 20)
            )
            for _ in range(products_count)
        ]
        Product.objects.bulk_create(products)

        self.stdout.write(self.style.SUCCESS("Database seeding complete."))