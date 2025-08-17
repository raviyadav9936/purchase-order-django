from django.core.management.base import BaseCommand
from shop.models import Product, Order
from decimal import Decimal
import random

class Command(BaseCommand):
    help = "Seed products and random orders"

    def handle(self, *args, **opts):
        Order.objects.all().delete()
        Product.objects.all().delete()

        products = []
        for i in range(1, 51):
            p = Product.objects.create(
                name=f"Product {i}",
                price=Decimal(random.randint(50, 5000)) / 1,
                stock_qty=random.randint(100, 1000),
            )
            products.append(p)

        # create orders
        for _ in range(5000):
            p = random.choice(products)
            qty = random.randint(1, 5)
            if p.stock_qty >= qty:
                p.stock_qty -= qty
                p.save()
                Order.objects.create(product=p, quantity=qty, total_price=p.price * qty)

        self.stdout.write(self.style.SUCCESS("Seeded products & orders"))
