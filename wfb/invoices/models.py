from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.core.validators import DecimalValidator

# internals
from wfb.core.models import Base

#  constants
User = get_user_model()


class InvoiceStatus(models.TextChoices):
    DRAFT = "DRAFT", _("DRAFT")
    SENT = "SENT", _("SENT")
    PAID = "PAID", _("PAID")

class Invoice(Base):
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    description = models.TextField()
    status = models.CharField(choices=InvoiceStatus.choices, max_length=10, default=InvoiceStatus.DRAFT)
    paid_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)

    professional = models.ForeignKey("users.Professional", on_delete=models.CASCADE, related_name="professional_invoices")
    client = models.ForeignKey("users.Client", on_delete=models.CASCADE, related_name="client_invoices")
    contract = models.ForeignKey("jobs.Contract", on_delete=models.CASCADE)

    class Meta:
        db_table = "t_invoice"