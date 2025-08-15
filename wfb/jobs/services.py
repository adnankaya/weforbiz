import logging
from decimal import Decimal

from django.db import transaction
from django.db.models import Q, QuerySet
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.conf import settings

from wfb.core.services import CoreService
from wfb.users.models import User, Profile, Client, Professional
from wfb.users.services import ProfessionalService
from wfb.notifications.services import NotificationService


from wfb.users.exceptions import TotalPointsNotEnoughException
from .models import Job, Proposal, Contract, FlaggedJob

logger = logging.getLogger(__name__)


class JobService(CoreService):
    @classmethod
    def accept_contract(cls, contract: Contract) -> Contract:
        """Professional accepts contract via this method"""
        if contract.status == Contract.Status.PENDING:
            with transaction.atomic():
                contract.status = Contract.Status.OPEN
                contract.workstatus = Job.Status.IN_PROGRESS
                contract.save()
                contract.proposal.is_accepted = True
                contract.proposal.save()
                try:
                    NotificationService.contract_accepted(contract)
                except Exception as e:
                    logger.exception(f"Could not send notification: {e}")

                return contract

    @classmethod
    def submit_work(cls, contract: Contract, validated_data) -> Contract:
        """Professional submits work contract via this method"""
        if contract.status == Contract.Status.OPEN:
            with transaction.atomic():
                contract.workstatus = Job.Status.IN_REVIEW
                # TODO implement better hours_worked
                contract.hours_worked = validated_data["hours_worked"] or 1
                contract.save()
                try:
                    NotificationService.work_submitted(contract)
                except Exception as e:
                    logger.exception(f"Could not send notification: {e}")
                return contract

    @classmethod
    def accept_work(cls, contract: Contract) -> Contract:
        """Client accepts work contract via this method"""
        if contract.status == Contract.Status.OPEN:
            with transaction.atomic():
                contract.workstatus = Job.Status.DONE
                contract.save()
                try:
                    NotificationService.work_accepted(contract)
                except Exception as e:
                    logger.exception(f"Could not send notification: {e}")
                return contract

    @classmethod
    def close_contract(cls, contract: Contract, closed_by, validated_data) -> Contract:
        """Professional or Client close contract via this method"""
        if contract.status == Contract.Status.OPEN:
            with transaction.atomic():
                contract.status = Contract.Status.CLOSED
                contract.close_reason = validated_data["reason"]
                contract.closed_by = closed_by
                contract.save()
                try:
                    NotificationService.contract_closed(contract)
                except Exception as e:
                    logger.exception(f"Could not send notification: {e}")
                return contract

    @classmethod
    def flag_job(
        cls, job: Job, professional: Professional, validated_data
    ) -> FlaggedJob:
        fjob = FlaggedJob.objects.create(
            job=job, reported_by=professional.user, **validated_data
        )
        return fjob

    @classmethod
    def create_job(cls, client: Client, validated_data) -> Job:
        with transaction.atomic():
            try:
                skills = validated_data.pop("skills")
                newjob = Job.objects.create(created_by=client, **validated_data)
                newjob.skills.set(skills)
                # newjob.save()
            except Exception as e:
                raise e
            else:
                return newjob

    @classmethod
    def create_contract(cls, job: Job, validated_data) -> Contract:
        try:
            proposal = validated_data.get("proposal")
            if Contract.objects.filter(job=job, proposal=proposal).exists():
                raise ValidationError(_("Contract for this proposal already exists!"))
            contract = Contract.objects.create(job=job, **validated_data)
            try:
                NotificationService.contract_created(contract)
            except Exception as e:
                logger.exception(f"Could not send notification: {e}")
        except Exception as e:
            raise e
        else:
            return contract

    @classmethod
    def create_proposal(cls, job: Job, user: User, validated_data) -> Proposal:
        if job.proposal_set.filter(created_by=user.professional).exists():
            raise ValidationError(_("Already applied this job"))

        professional = user.professional
        with transaction.atomic():
            try:
                ProfessionalService.update_points(professional, job)
            except TotalPointsNotEnoughException as te:
                raise te
            proposal = Proposal(created_by=professional, job=job, **validated_data)
            proposal.commission = Decimal(settings.COMMISSION)
            proposal.service_fee = proposal.amount * (proposal.commission / 100)
            proposal.total_result = proposal.amount - proposal.service_fee
            proposal.save()
            try:
                NotificationService.proposal_created(proposal)
            except Exception as e:
                logger.exception(f"Could not send notification: {e}")

            return proposal

    @classmethod
    def search(cls, qs_jobs: QuerySet, query: str, *args, **kwargs) -> QuerySet:
        """
        TODO : will add full text search
        """
        res = qs_jobs.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

        return res


###############################################################################
##################     Sorting Service    ##############################
###############################################################################


class SortingService:
    def __init__(self, strategy):
        self.strategy = strategy

    def set_strategy(self, strategy):
        self.strategy = strategy

    def sort_data(self, qs_data):
        return self.strategy.sort(qs_data)


###############################################################################
##################     Job Listing Service    ##############################
###############################################################################


class JobListingService:
    def __init__(self):
        self.observers = []

    def attach(self, observer):
        self.observers.append(observer)

    def detach(self, observer):
        self.observers.remove(observer)

    def notify_observers(self, professional):
        for observer in self.observers:
            observer.notify(professional)

    def create_job_listing(self, job_listing):
        # Logic to create job listing

        # Notify all observers
        self.notify_observers(job_listing.professional)
