from decimal import Decimal
from django.utils import timezone
from django.db import models
from django.core.validators import (MinValueValidator, MinLengthValidator,
                                    MaxLengthValidator, MaxValueValidator)
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _


# internals
User = get_user_model()

class EmailTemplate(models.Model):
    name = models.CharField(max_length=64)
    subject = models.CharField(max_length=140)
    body = models.TextField()

    class Meta:
        db_table = "t_email_template"