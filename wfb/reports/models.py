from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.core.validators import DecimalValidator
from decimal import Decimal

# internals
from wfb.core.models import Base
#  constants
User = get_user_model()


class Report(Base):
    start_date = models.DateField()
    end_date = models.DateField()
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Type(models.TextChoices):
        WEEKLY = "WEEKLY", _("WEEKLY")
        MONTHLY = "MONTHLY", _("MONTHLY")
        YEARLY = "YEARLY", _("YEARLY")

    report_type = models.CharField(choices=Type.choices, max_length=10,
                                   default=Type.MONTHLY)

    class Meta:
        db_table = "t_report"
