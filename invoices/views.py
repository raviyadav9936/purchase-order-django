import datetime
from decimal import Decimal
import json
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.db.models import Sum
from django.utils.dateparse import parse_date
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import PurchaseOrder
from .serializers import PurchaseOrderSerializer
from .ocr import extract_text_from_pdf
from .parsers import extract_fields


def convert_for_json(obj):
    """Recursively convert date/datetime to string and Decimal to float."""
    if isinstance(obj, dict):
        return {k: convert_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_for_json(i) for i in obj]
    elif isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj

def upload_view(request):
    if request.method == "POST":
        f = request.FILES.get("file")
        if not f:
            return render(request, "invoices/upload.html", {"error": "Please choose a PDF/Image file."})

        po = PurchaseOrder(source_file=f)
        po.save()

        text = extract_text_from_pdf(po.source_file.path)
        fields = extract_fields(text)

        # Normalize keys
        fields_normalized = {k.lower().replace(" ", "_").replace(".", ""): v for k, v in fields.items()}

        # Update model fields
        for k, v in fields_normalized.items():
            if hasattr(po, k):
                setattr(po, k, v)

        # Save extracted JSON safely
        po.extracted_json = {
            "text_preview": text[:2000],
            "fields": convert_for_json(fields_normalized)
        }
        po.save()

        return redirect("dashboard")

    return render(request, "invoices/upload.html")



def dashboard_view(request):
    # Get filter values
    date_from = request.GET.get("from")
    date_to = request.GET.get("to")

    qs = PurchaseOrder.objects.all().order_by("-created_at")

    # Safely parse dates
    parsed_from = parse_date(date_from) if date_from else None
    parsed_to = parse_date(date_to) if date_to else None

    if parsed_from:
        qs = qs.filter(po_date__gte=parsed_from)
    if parsed_to:
        qs = qs.filter(po_date__lte=parsed_to)

    # Caching for aggregation
    cache_key = f"po_agg:{date_from}:{date_to}"
    agg = cache.get(cache_key)
    if agg is None:
        agg = (
            qs.values("po_date")
              .annotate(total_per_day=Sum("grand_total"))
              .order_by("po_date")
        )
        agg = list(agg)
        agg = convert_for_json(agg)
        cache.set(cache_key, agg, timeout=60)

    return render(request, "invoices/dashboard.html", {
        "orders": qs[:500],  
        "agg": json.dumps(agg),
        "filter_from": date_from or "",
        "filter_to": date_to or "",
    })


# ----- API -----
@api_view(["GET"])
def purchase_order_api(request):
    date_from = request.GET.get("from")
    date_to = request.GET.get("to")

    qs = PurchaseOrder.objects.all().order_by("-created_at")
    if date_from:
        qs = qs.filter(po_date__gte=date_from)
    if date_to:
        qs = qs.filter(po_date__lte=date_to)

    ser = PurchaseOrderSerializer(qs, many=True)
    return Response(ser.data, status=status.HTTP_200_OK)
