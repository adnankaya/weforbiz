from django.db import models
from django.core.cache import cache
from django.apps import apps
from django.db.models.query import QuerySet
from django.db.models import OuterRef, Exists, Q, F, Sum


class ContractObjectsManager(models.Manager):
    def get_queryset(self) -> QuerySet:
        qs_core = super().get_queryset()
        qs = qs_core.select_related(
            "job", "job__created_by", "proposal", "proposal__created_by"
        ).annotate(
            total_amount=Sum(F("proposal__amount") * F("hours_worked"))
        ).order_by("-created_date")
        return qs

    def with_feedback(self, user):
        Feedback = apps.get_model("feedbacks", "Feedback")
        # Subquery to check if user has submitted a feedback before
        qs_sub = Feedback.objects.filter(contract=OuterRef("pk"), created_by=user)
        return self.annotate(is_feedback_submitted=Exists(qs_sub))
