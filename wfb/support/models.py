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


class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    description = models.TextField()
    subject = models.TextField()

    class PriorityStatus(models.TextChoices):
        LOW = "LOW", _("LOW")
        MEDIUM = "MEDIUM", _("MEDIUM")
        HIGH = "HIGH", _("HIGH")
    priority = models.CharField(choices=PriorityStatus.choices, max_length=10,
                                default=PriorityStatus.LOW)

    class TicketStatus(models.TextChoices):
        OPEN = "OPEN", _("OPEN")
        RESOLVED = "RESOLVED", _("RESOLVED")
        CLOSED = "CLOSED", _("CLOSED")
    status = models.CharField(choices=TicketStatus.choices, max_length=10,
                              default=TicketStatus.OPEN)

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    created_date = models.DateTimeField(auto_now_add=True)
    resolved_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 't_ticket'
