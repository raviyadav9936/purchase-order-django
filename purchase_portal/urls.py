from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls), 
    path("api/shop/", include("shop.urls")), 
    path("api/invoices/", include("invoices.urls")),
    path("", include("invoices.urls")),
]
