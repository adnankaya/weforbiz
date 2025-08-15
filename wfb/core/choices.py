from django.db import models
from django.utils.translation import gettext_lazy as _
from datetime import timedelta


class ExperienceLevel(models.TextChoices):
    BEGINNER = "BEGINNER", _("BEGINNER")
    INTERMEDIATE = "INTERMEDIATE", _("INTERMEDIATE")
    EXPERT = "EXPERT", _("EXPERT")


class Duration(models.TextChoices):
    ONE_HOUR = '1_hour', _('1 hour')
    TWENTY_FOUR_HOURS = '24_hours', _('24 hours')
    THREE_DAYS = '3_days', _('3 days')
    ONE_WEEK = '1_week', _('1 week')
    ONE_MONTH = '1_month', _('1 month')
    THREE_MONTHS = '3_months', _('3 months')
    SIX_MONTHS = '6_months', _('6 months')

    def calculate_timedelta(self):
        DURATION_MAP = {
            self.ONE_HOUR: timedelta(hours=1),
            self.TWENTY_FOUR_HOURS: timedelta(days=1),
            self.THREE_DAYS: timedelta(days=3),
            self.ONE_WEEK: timedelta(weeks=1),
            self.ONE_MONTH: timedelta(days=30),
            self.THREE_MONTHS: timedelta(days=90),
            self.SIX_MONTHS: timedelta(days=180),
        }
        return DURATION_MAP.get(self, timedelta(0))
