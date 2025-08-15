
from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.db.models import EmailField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from django.db import models
from django.db.models import Count, Avg, Sum, F, Q, Prefetch

from wfb.core.models import BaseUuidModel
from wfb.jobs.models import Contract, Job
from wfb.feedbacks.models import Feedback, Rating
from .managers import UserManager


class User(AbstractUser):
    """
    Default custom user model for weforbiz.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    email = EmailField(_("email address"), unique=True)
    username = None  # type: ignore[assignment]
    first_name = models.CharField(blank=True, null=True, max_length=255)
    last_name = models.CharField(blank=True, null=True, max_length=255)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})

    @property
    def client(self):
        return self.client_set.first()

    @property
    def professional(self):
        return self.professional_set.first()

    @classmethod
    def get_system_user(cls):
        return cls.objects.get(username="system-user")
    

class Profile(BaseUuidModel):
    class Types(models.TextChoices):
        FREELANCER = "FREELANCER", _("FREELANCER")
        CLIENT = "CLIENT", _("CLIENT")

    profile_type = models.CharField(
        max_length=10, choices=Types.choices, default=Types.FREELANCER
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(
        "address.Address", on_delete=models.SET_NULL, null=True, blank=True
    )
    phone = models.CharField(max_length=32, null=True, blank=True)
    # timezone = models.CharField(max_length=16)#TODO

    class Meta:
        unique_together = ["user", "profile_type"]
        abstract = True

    # TODO remove
    def get_msg_count(self):
        import random
        return random.randint(1, 10)

    def get_previous_contracts(self):
        raise NotImplementedError()

    @property
    def feedback_count(self):
        qs_pc = self.get_previous_contracts()
        return (
            qs_pc.aggregate(
                fc=Count("feedback", filter=~Q(feedback__created_by=self.user))
            ).get("fc")
            or 0
        )

    @property
    def total_avg_rating(self):
        qs_pc = self.get_previous_contracts()
        agg_res = qs_pc.aggregate(average_rating=Avg("feedback__responses__rating", filter=~Q(feedback__created_by=self.user)))
        res = agg_res["average_rating"] or 0
        return round(res, 2)


class Professional(Profile):
    class VisibilityChoices(models.TextChoices):
        PUBLIC = "PUBLIC", _("Public")
        PLATFORM_ONLY = "PLATFORM ONLY", _("Platform Only")
        PRIVATE = "PRIVATE", _("Private")

    class Badges(models.TextChoices):
        NONE = "NONE", _("NONE")
        RISING_STAR = "RISING STAR", _("RISING STAR")
        TALENTED = "TALENTED", _("TALENTED")
        EXPERT = "EXPERT", _("EXPERT")
        MASTER = "MASTER", _("MASTER")
        ELITE = "ELITE", _("ELITE")

    visibility = models.CharField(
        max_length=13,
        choices=VisibilityChoices.choices,
        default=VisibilityChoices.PLATFORM_ONLY,
    )
    badge = models.CharField(max_length=11, choices=Badges.choices, default=Badges.NONE)
    hourly_rate = models.DecimalField(default=10, max_digits=6, decimal_places=2)
    title = models.CharField(max_length=64, null=True, blank=True, default="")
    bio = models.TextField(null=True, blank=True, default="")
    skills = models.ManyToManyField("core.Skill")
    is_available = models.BooleanField(default=True)
    balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total_points = models.PositiveSmallIntegerField(default=50)
    hoursperweek = models.PositiveSmallIntegerField(default=40)

    class Meta:
        db_table = "t_professional"

    def get_absolute_url(self):
        return reverse("users:professionals-detail", args=(self.id,))

    def skill_names(self):
        return self.skills.values_list("name", flat=True)

    def skill_names_comma_separated(self):
        return ",".join(s for s in self.skill_names())

    @property
    def positive_feedback_count(self):
        """Number of positive feedbacks (rating 4 or 5)"""
        return self.aggregate_positive_feedback()["positive_count"]

    @property
    def positive_feedback_avg_rating(self):
        """Number of positive feedbacks (rating 4 or 5)"""
        return self.aggregate_positive_feedback()["average_rating"]

    def aggregate_positive_feedback(self):
        """positive feedbacks (rating 4 or 5)"""
        qs_pc = self.get_previous_contracts()
        Q_positive = Q(feedback__responses__rating__in=[Rating.FOUR, Rating.FIVE])
        Q_only_client_feedbacks = ~Q(feedback__created_by=self.user)
        agg_res = qs_pc.aggregate(
            average_rating=Avg(
                "feedback__responses__rating",
                filter=Q_positive & Q_only_client_feedbacks,
            ),
            positive_count=Count(
                "feedback__responses", filter=Q_positive & Q_only_client_feedbacks
            ),
        )
        return agg_res

    @property
    def recurring_client_count(self):
        qs_pc = self.get_previous_contracts()
        res = qs_pc.aggregate(
            client_count=Count("job__created_by")
            - Count("job__created_by", distinct=True)
        )
        return res["client_count"] or 0

    @property
    def total_hours_worked(self):
        qs_pc = self.get_previous_contracts()
        res = qs_pc.aggregate(sum_hours_worked=Sum("hours_worked"))
        return res.get("sum_hours_worked") or 0

    def get_previous_contracts(self):
        res = (
            Contract.objects.filter(
                proposal__created_by=self, workstatus=Job.Status.DONE
            )
            .select_related(
                "proposal",
                "job",
            )
            .prefetch_related(
                Prefetch(
                    "feedback_set",
                    queryset=Feedback.objects.exclude(created_by=self.user),
                )
            )
        )
        return res

    @property
    def completion_rate(self):
        all_proposals_count = self.proposal_set.count()
        completeds_count = self.completed_jobs_count
        if all_proposals_count > 0 and completeds_count > 0:
            return round((completeds_count / all_proposals_count) * 100)
        return 0

    @property
    def completed_jobs_count(self):
        qs_pc = self.get_previous_contracts()
        return qs_pc.count()

    @property
    def submitted_proposals_count(self):
        res = self.proposal_set.filter(is_accepted=False).count()
        return res

    @property
    def active_contracts_count(self):
        res = Contract.objects.filter(
            proposal__created_by=self, status=Contract.Status.OPEN
        ).count()
        return res

    @property
    def success_score(self):
        # Response time (you'll need to define a field to store message timestamps)
        # For example, assuming you have a 'messages' field in your Proposal model:
        # response_times = self.response_time # TODO

        # Define WEIGHTAGE FOR the new metrics
        WEIGHTAGE_RATING = 0.4
        WEIGHTAGE_COMPLETED_PROJECTS = 0.2
        WEIGHTAGE_EARNINGS = 0.1
        WEIGHTAGE_POSITIVE_FEEDBACKS = 0.1
        WEIGHTAGE_RECURRING_CLIENTS = 0.1
        # WEIGHTAGE_RESPONSE_TIME = 0.1 # TODO
        WEIGHTAGE_COMPLETION_RATE = 0.1

        # Calculate the job success score with the new metrics
        res = (
            WEIGHTAGE_RATING * self.total_avg_rating
            + WEIGHTAGE_COMPLETED_PROJECTS * self.completed_jobs_count
            + WEIGHTAGE_EARNINGS * float(self.total_earnings_amount)
            + WEIGHTAGE_POSITIVE_FEEDBACKS * self.positive_feedback_count
            + WEIGHTAGE_RECURRING_CLIENTS * self.recurring_client_count
            # + WEIGHTAGE_RESPONSE_TIME * response_times # TODO
            + WEIGHTAGE_COMPLETION_RATE * self.completion_rate
        )

        return round(res, 2)

    @property
    def total_earnings_amount(self):
        qs_pc = self.get_previous_contracts()
        res = qs_pc.aggregate(
            total_amount=Sum(F("proposal__amount") * F("hours_worked"))
        )
        return res.get("total_amount") or 0

    @property
    def total_earnings_result(self):
        qs_pc = self.get_previous_contracts()
        res = qs_pc.aggregate(
            total_result=Sum(F("proposal__total_result") * F("hours_worked"))
        )
        return res.get("total_result") or 0


class Client(Profile):
    # this field will be calculated automatically
    spent = models.DecimalField(default=0, max_digits=18, decimal_places=2)
    # what information client may have ?
    # company = models.ForeignKey(Company, on_delete=models.CASCADE) # TODO add later

    class Meta:
        db_table = "t_client"

    def get_absolute_url(self):
        return reverse("users:clients-detail", args=(self.id,))

    def get_previous_contracts(self):
        res = (
            Contract.objects.filter(job__created_by=self, workstatus=Job.Status.DONE)
            .select_related(
                "proposal",
                "job",
            )
            .prefetch_related(
                Prefetch(
                    "feedback_set",
                    queryset=Feedback.objects.all(),
                    # queryset=Feedback.objects.filter(created_by=self.user),
                )
            )
        )

        return res

    @property
    def posted_jobs_count(self):
        return self.job_set.count()

    @property
    def total_spent(self):
        qs_pc = self.get_previous_contracts()
        res = qs_pc.aggregate(
            total_amount=Sum(F("proposal__amount") * F("hours_worked"))
        )
        res = res.get("total_amount") or 0
        return res


class Portfolio(models.Model):
    professional = models.ForeignKey("users.Professional", on_delete=models.CASCADE)
    title = models.CharField(max_length=64)
    description = models.TextField()
    link = models.URLField(null=True, blank=True)

    class Meta:
        db_table = "t_portfolio"


class Education(models.Model):
    professional = models.ForeignKey("users.Professional", on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    area_of_study = models.CharField(max_length=64)
    degree = models.CharField(max_length=64)
    school_name = models.CharField(max_length=64)

    class Meta:
        db_table = "t_education"


class Experience(models.Model):
    professional = models.ForeignKey("users.Professional", on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    job_title = models.CharField(max_length=64)
    company_name = models.CharField(max_length=64)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "t_experience"


class Certification(models.Model):
    professional = models.ForeignKey("users.Professional", on_delete=models.CASCADE)
    acquired_date = models.DateField()
    name = models.CharField(max_length=64)
    authority = models.CharField(max_length=64)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "t_certification"


class Availability(models.Model):
    professional = models.ForeignKey("users.Professional", on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "t_availability"

