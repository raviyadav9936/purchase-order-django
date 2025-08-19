from django.db import models

class PurchaseOrder(models.Model):
    po_number = models.CharField(max_length=64, db_index=True)       
    po_date = models.DateField(null=True, blank=True)                
    grand_total = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)  
    source_file = models.FileField(upload_to="po_uploads/")       
    created_at = models.DateTimeField(auto_now_add=True)            

    class Meta:
        indexes = [
            models.Index(fields=["po_number"]),
            models.Index(fields=["po_date"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.po_number} ({self.po_date})"
