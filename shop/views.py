from django.db import transaction
from django.db.models import F, Sum
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product, Order
from .serializers import ProductSerializer, OrderSerializer, TopProductSerializer

@api_view(["POST"])
def add_product(request):
    ser = ProductSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    product = ser.save()
    return Response(ProductSerializer(product).data, status=201)

@api_view(["POST"])
def place_order(request):
    """
    Body: {product: <id>, quantity: <int>}
    - auto-calculates total_price
    - reduces stock atomically
    - error on insufficient stock
    """
    product_id = request.data.get("product")
    qty = int(request.data.get("quantity", 0))
    if not product_id or qty <= 0:
        return Response({"detail":"product & positive quantity required"}, status=400)

    with transaction.atomic():
        product = Product.objects.select_for_update().get(id=product_id)
        if product.stock_qty < qty:
            return Response({"detail":"Insufficient stock"}, status=400)
        product.stock_qty = F("stock_qty") - qty
        product.save(update_fields=["stock_qty"])

        total_price = product.price * qty
        order = Order.objects.create(product=product, quantity=qty, total_price=total_price)

    return Response(OrderSerializer(order).data, status=201)

@api_view(["GET"])
def top_products(request):
    """
    Aggregate by product with index support; optimized for large datasets.
    SELECT product_id, SUM(quantity) AS total_sold
    FROM shop_order GROUP BY product_id ORDER BY total_sold DESC LIMIT 10;
    """
    qs = (Order.objects
          .values("product_id","product__name")
          .annotate(total_sold=Sum("quantity"))
          .order_by("-total_sold")[:10])

    data = [{"product_id": r["product_id"], "name": r["product__name"], "total_sold": r["total_sold"]} for r in qs]
    return Response(TopProductSerializer(data, many=True).data)

@api_view(["GET"])
def revenue_per_product(request):
    """
    Single SQL query returning total revenue per product.
    """
    from django.db import connection
    sql = """
        SELECT p.id AS product_id, p.name, COALESCE(SUM(o.total_price), 0) AS revenue
        FROM shop_product p
        LEFT JOIN shop_order o ON o.product_id = p.id
        GROUP BY p.id, p.name
        ORDER BY revenue DESC;
    """
    with connection.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    result = [{"product_id": r[0], "name": r[1], "revenue": float(r[2])} for r in rows]
    return Response(result)
