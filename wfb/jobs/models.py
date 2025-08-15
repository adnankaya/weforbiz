from collections.abc import Iterable
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
from django.urls import reverse
from django.utils import timezone
from slugify import slugify
from django.db import transaction
from wfb.core.models import BaseModel, BaseUuidModel
from .managers import ContractObjectsManager


class Job(BaseUuidModel):
    class Type(models.TextChoices):
        FIXED = "FIXED", _("FIXED")
        HOURLY = "HOURLY", _("HOURLY")

    class Status(models.TextChoices):
        TODO = "TODO", _("TODO")
        IN_PROGRESS = "IN PROGRESS", _("IN PROGRESS")
        IN_REVIEW = "IN REVIEW", _("IN REVIEW")
        CHANGE_REQUEST = "CHANGE REQUEST", _("CHANGE REQUEST")
        DONE = "DONE", _("DONE")

    slug = models.SlugField(max_length=256, unique_for_date="created_date")
    status = models.CharField(
        default=Status.TODO, max_length=14, choices=Status.choices
    )
    title = models.CharField(max_length=140)
    description = models.TextField()
    skills = models.ManyToManyField("core.Skill")
    min_budget = models.DecimalField(
        default=0, max_digits=3, decimal_places=0, validators=[MinValueValidator(0)]
    )
    max_budget = models.DecimalField(
        default=10, max_digits=9, decimal_places=0, validators=[MinValueValidator(10)]
    )
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    job_type = models.CharField(max_length=6, choices=Type.choices, default=Type.FIXED)
    created_by = models.ForeignKey("users.Client", on_delete=models.CASCADE)
    required_points = models.PositiveSmallIntegerField(default=4)

    class Meta:
        db_table = "t_job"
        ordering = ["-created_date"]

    def __str__(self) -> str:
        return self.title

    def process_slugify(self):
        self.slug = f"{slugify(self.title)}_{str(self.id)}"

    def save(self, *args, **kwargs):
        try:
            with transaction.atomic():
                self.process_slugify()
                super(Job, self).save(*args, **kwargs)
        except Exception as e:
            raise e

    def get_absolute_url(self):
        return reverse(
            "jobs:detail",
            args=[
                self.slug,
            ],
        )

    @property
    def proposal_count(self):
        return self.proposal_set.count()

    @property
    def last_viewed_date(self):
        qs = (
            self.proposal_set.filter(viewed_date__isnull=False)
            .order_by("-viewed_date")
            .values_list("viewed_date", flat=True)
            .first()
        )
        return qs

    @property
    def hired(self):
        qs = self.contract_set.filter(
            status__in=[Contract.Status.OPEN, Contract.Status.CLOSED]
        ).count()
        return qs


class Proposal(BaseUuidModel):
    created_by = models.ForeignKey("users.Professional", on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        help_text=_("Professional proposal amount to complete the job"),
    )
    commission = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MaxValueValidator(100)],
        help_text=_("Commission Percentage Rate. Ex; 10"),
    )
    service_fee = models.DecimalField(
        max_digits=18, decimal_places=2, help_text=_("Platform Service Fee")
    )
    total_result = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        help_text=_("Total Professional Money"),
    )
    coverletter = models.TextField()
    is_accepted = models.BooleanField(default=False)
    viewed_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_(
            "View date when a client view the proposal we need to set this field"
        ),
    )

    class Meta:
        db_table = "t_proposal"
        unique_together = [["created_by", "job"]]

    def save(self, *args, **kwargs) -> None:
        self.calculate_result()
        if not self.service_fee < self.total_result < self.amount:
            raise ValidationError(
                _("Expected calculation is commission < total_result < amount")
            )
        return super().save(*args, **kwargs)

    def calculate_result(self):
        self.total_result = self.amount - self.service_fee

    def get_absolute_url(self):
        return reverse(
            "jobs:proposal-detail",
            args=(
                self.job.id,
                self.id,
            ),
        )


class Contract(BaseUuidModel):
    class Status(models.TextChoices):
        PENDING = "PENDING", _("PENDING")
        OPEN = "OPEN", _("OPEN")
        CLOSED = "CLOSED", _("CLOSED")

    status = models.CharField(
        default=Status.PENDING, max_length=7, choices=Status.choices
    )

    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE)
    workstatus = models.CharField(
        default=Job.Status.TODO, max_length=14, choices=Job.Status.choices
    )
    hours_worked = models.PositiveSmallIntegerField(default=1)
    close_reason = models.TextField(null=True, blank=True)
    closed_by = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, null=True, blank=True
    )

    # description = models.TextField(null=True, blank=True) TODO

    obs = ContractObjectsManager()

    class Meta:
        db_table = "t_contract"
        unique_together = [["job", "proposal"]]

    def __str__(self) -> str:
        return f"{self.status}"

    def get_absolute_url(self):
        return reverse("jobs:contracts-detail", args=(self.id,))

    @property
    def client_user(self):
        return self.job.created_by.user

    @property
    def professional_user(self):
        return self.proposal.created_by.user

    def save(self, *args, **kwargs) -> None:
        if self.is_hours_worked_one_hour_for_fixed_jobs():
            raise ValidationError(_("hours_worked must be 1 for FIXED jobs!"))
        return super().save(*args, **kwargs)

    def is_hours_worked_one_hour_for_fixed_jobs(self):
        """return True if fixed job hours_worked is 1"""
        return (self.job.job_type == self.job.Type.FIXED) and not (
            self.hours_worked == 1
        )


class FlaggedJob(models.Model):
    job = models.ForeignKey("Job", on_delete=models.CASCADE)
    reason = models.TextField(
        _("Reason"), null=True, blank=True, validators=[MaxLengthValidator(280)]
    )
    reported_by = models.ForeignKey(
        "users.User",
        related_name="reported_flagged_jobs",
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = "t_flagged_job"
        unique_together = ["job", "reported_by"]


class ProfessionalSavedJob(models.Model):
    job = models.ForeignKey("Job", on_delete=models.CASCADE)

    saved_by = models.ForeignKey(
        "users.Professional",
        related_name="professional_saved_jobs",
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = "t_professional_saved_job"
        unique_together = ["job", "saved_by"]
