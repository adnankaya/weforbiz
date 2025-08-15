from decimal import Decimal
from django.utils import timezone
from django.db import models
from django.core.validators import (MinValueValidator, MinLengthValidator,
                                    MaxLengthValidator, MaxValueValidator)
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

# internals
from wfb.core.models import Base


# internals
User = get_user_model()


class PromotionType(Base):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "t_promotion_type"


class Promotion(Base):
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    amount = models.DecimalField(max_digits=9, decimal_places=2,
                                 validators=[MinValueValidator(Decimal('0.00'))])
    promotion_type = models.ForeignKey(PromotionType, on_delete=models.PROTECT)

    class Meta:
        db_table = "t_promotion"


class UserPromotion(Base):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE)

    class Status(models.TextChoices):
        PENDING = "PENDING", _("PENDING")
        APPROVED = "APPROVED", _("APPROVED")
        REJECTED = "REJECTED", _("REJECTED")

    status = models.CharField(choices=Status.choices, max_length=10,
                              default=Status.PENDING)

    class Meta:
        db_table = "t_user_promotion"
