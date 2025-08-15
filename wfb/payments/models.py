from decimal import Decimal
from django.utils import timezone
from django.db import models
from django.core.validators import (
    MinValueValidator,
    MinLengthValidator,
    MaxLengthValidator,
    MaxValueValidator,
)
from django.utils.translation import gettext_lazy as _


# internals
from wfb.core.models import BaseModel, BaseUuidModel


class PaymentMethod(models.TextChoices):
    PENDING = "PENDING", _("PENDING")
    PAYPAL = "PAYPAL", _("PAYPAL")
    IYZICO = "IYZICO", _("IYZICO")
    CREDIT_CARD = "CREDIT CARD", _("CREDIT CARD")
    BANK_TRANSFER = "BANK TRANSFER", _("BANK TRANSFER")


class ResponseStatus(models.TextChoices):
    SUCCESS = "success", _("success")
    ERROR = "error", _("error")


class Currency(models.Model):
    code = models.CharField(max_length=4, unique=True)
    name = models.CharField(max_length=32, unique=True)

    class Meta:
        db_table = "t_currency"


class UserPaymentMethod(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    payment_method = models.CharField(
        choices=PaymentMethod.choices, max_length=13, default=PaymentMethod.IYZICO
    )

    class Meta:
        db_table = "t_user_payment_method"


class PaymentStatus(models.TextChoices):
    PENDING = "PENDING", _("PENDING")
    COMPLETED = "COMPLETED", _("COMPLETED")
    REFUNDED = "REFUNDED", _("REFUNDED")
    FAILED = "FAILED", _("FAILED")


class Payment(BaseModel):
    contract = models.ForeignKey("jobs.Contract", on_delete=models.CASCADE)
    amount = models.DecimalField(
        max_digits=9, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )
    payment_method = models.CharField(choices=PaymentMethod.choices, max_length=13)
    status = models.CharField(
        choices=PaymentStatus.choices, max_length=10, default=PaymentStatus.PENDING
    )

    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "t_payment"


class Transaction(BaseUuidModel):
    class Type(models.TextChoices):
        MEMBERSHIP_FEE = "MEMBERSHIP FEE", _("MEMBERSHIP FEE")
        SERVICE_FEE = "SERVICE FEE", _("SERVICE FEE")
        WITHDRAWAL_FEE = "WITHDRAWAL FEE", _("WITHDRAWAL FEE")
        WITHDRAWAL = "WITHDRAWAL", _("WITHDRAWAL")
        REFUND = "REFUND", _("REFUND")

    transaction_type = models.CharField(
        choices=Type.choices,
        max_length=24,
        default=Type.SERVICE_FEE,
    )
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT)
    amount = models.DecimalField(
        max_digits=9, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )

    status = models.CharField(
        choices=PaymentStatus.choices, max_length=10, default=PaymentStatus.PENDING
    )
    description = models.TextField()

    class Meta:
        db_table = "t_transaction"


class Withdrawal(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT)
    amount = models.DecimalField(
        max_digits=9, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )
    payment_method = models.CharField(choices=PaymentMethod.choices, max_length=13)
    created_date = models.DateTimeField(auto_now_add=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        choices=PaymentStatus.choices, max_length=10, default=PaymentStatus.PENDING
    )

    class Meta:
        db_table = "t_withdrawal"


class Escrow(models.Model):
    """Emanet"""

    class EscrowStatus(models.TextChoices):
        PENDING = "PENDING", _("PENDING")
        COMPLETED = "COMPLETED", _("COMPLETED")
        REFUNDED = "REFUNDED", _("REFUNDED")
        FAILED = "FAILED", _("FAILED")

    contract = models.ForeignKey("jobs.Contract", on_delete=models.PROTECT)
    amount = models.DecimalField(
        max_digits=9, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )
    created_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        choices=EscrowStatus.choices, max_length=10, default=EscrowStatus.PENDING
    )

    class Meta:
        db_table = "t_escrow"
