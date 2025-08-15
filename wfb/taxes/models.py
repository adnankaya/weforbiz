from decimal import Decimal
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


class Tax(Base):
    invoice = models.ForeignKey("invoices.Invoice", on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=9, decimal_places=2,
                                 validators=[MinValueValidator(Decimal('0.00'))])
    country = models.ForeignKey("address.Country", on_delete=models.PROTECT)
    tax_number = models.CharField(max_length=64)
    class Meta:
        db_table = "t_tax"