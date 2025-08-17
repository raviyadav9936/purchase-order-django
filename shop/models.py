from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock_qty = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="orders")
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=14, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["product", "order_date"], name="order_prod_date_idx"),
        ]

    def __str__(self):
        return f"Order #{self.id} - {self.product.name}"
