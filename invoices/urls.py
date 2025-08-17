from django.urls import path
from .views import upload_view, dashboard_view, purchase_order_api

urlpatterns = [
    path("", dashboard_view, name="dashboard"),
    path("upload/", upload_view, name="upload"),
    path("purchase_order/", purchase_order_api, name="purchase_order_api"),
]
