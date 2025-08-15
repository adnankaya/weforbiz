from decimal import Decimal
from django.utils import timezone
from django.db import models
from django.core.validators import (MinValueValidator, MinLengthValidator,
                                    MaxLengthValidator, MaxValueValidator)
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _


# internals
User = get_user_model()

class Billing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_method = models.ForeignKey("payments.PaymentMethod", on_delete=models.CASCADE)
    billing_address = models.ForeignKey("address.UserAddress", on_delete=models.CASCADE)
    zip = models.CharField(max_length=120)

    class Meta:
        db_table = "t_billing"


class BillingHistory(models.Model):
    class BillingStatus(models.TextChoices):
        PENDING = "PENDING", _("PENDING")
        COMPLETED = "COMPLETED", _("COMPLETED")
        REFUNDED = "REFUNDED", _("REFUNDED")
        FAILED = "FAILED", _("FAILED")

    status = models.CharField(choices=BillingStatus.choices, max_length=10,
                              default=BillingStatus.PENDING)
    payment_method = models.ForeignKey("payments.PaymentMethod", on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=9, decimal_places=2,
                                 validators=[MinValueValidator(Decimal('0.00'))])
    created_date = models.DateTimeField(auto_now_add=True)
    
    description = models.TextField()
    client = models.ForeignKey("users.Client", on_delete=models.CASCADE)
    professional = models.ForeignKey("users.Professional", on_delete=models.CASCADE)

    class Meta:
        db_table = "t_billing_history"