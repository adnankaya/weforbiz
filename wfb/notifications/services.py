from django.conf import settings
from django.utils.translation import gettext as _
from wfb.users.models import User
from wfb.jobs.models import Contract, Proposal
from wfb.notifications.signals import notify
from .strategies import (
    NotificationStrategy,
    EmailNotificationStrategy,
    SMSNotificationStrategy,
    PushNotificationStrategy,
)


class NotificationService:
    def __init__(self, strategy: NotificationStrategy):
        self.strategy = strategy

    def send_notification(self, user, message):
        self.strategy.send_notification(user, message)

    @classmethod
    def proposal_viewed(cls, proposal: Proposal):
        c_professional = proposal.created_by.user
        user = User.objects.get(email=f"notifier@{settings.DOMAIN}")
        verb = _("Your proposal has been viewed")
        description = _(
            "Good news! The client viewed your proposal. Now it's time to wait for contract"
        )
        extra_data = {
            "action": {"url": proposal.get_absolute_url(), "title": _("View Proposal")}
        }
        notify.send(
            sender=user,
            recipient=c_professional,
            verb=verb,
            description=description,
            **extra_data,
        )

    @classmethod
    def proposal_created(cls, proposal: Proposal):
        professional = proposal.created_by
        c_user = proposal.job.created_by.user
        user = User.objects.get(email=f"notifier@{settings.DOMAIN}")
        verb = _(
            "{} sent proposal for {}".format(
                professional.user.get_full_name(), proposal.job.title
            )
        )
        description = _("You can check it out and hire the professional.")
        extra_data = {
            "action": {"url": proposal.get_absolute_url(), "title": _("View Proposal")}
        }

        notify.send(
            sender=user,
            recipient=c_user,
            verb=verb,
            description=description,
            **extra_data,
        )

    @classmethod
    def contract_created(cls, contract: Contract):
        f_user = contract.professional_user
        c_user = contract.job.created_by.user
        user = User.objects.get(email=f"notifier@{settings.DOMAIN}")
        verb = _(
            "{} sent contract for {}".format(c_user.get_full_name(), contract.job.title)
        )
        description = _(
            "The client sent the contract. You can accept and start working."
        )
        extra_data = {
            "action": {"url": contract.get_absolute_url(), "title": _("View Contract")}
        }

        notify.send(
            sender=user,
            recipient=f_user,
            verb=verb,
            description=description,
            **extra_data,
        )

    @classmethod
    def contract_accepted(cls, contract: Contract):
        """Notify the client when professional accepted the contract"""
        c_user = contract.client_user
        user = User.objects.get(email=f"notifier@{settings.DOMAIN}")
        verb = _("Contract {} has been accepted".format(contract.job.title))
        description = _("The professional accepted the contract.")
        extra_data = {
            "action": {"url": contract.get_absolute_url(), "title": _("View Contract")}
        }

        notify.send(
            sender=user,
            recipient=c_user,
            verb=verb,
            description=description,
            **extra_data,
        )

    @classmethod
    def contract_closed(cls, contract: Contract):
        """Notify to the user when contract has been closed"""
        recipient = (
            contract.professional_user
            if contract.closed_by == contract.client_user
            else contract.client_user
        )
        user = User.objects.get(email=f"notifier@{settings.DOMAIN}")
        verb = _("Contract '{}' has been closed".format(contract.job.title))
        description = _("You can give feedback now.")
        extra_data = {
            "action": {"url": contract.get_absolute_url(), "title": _("View Contract")}
        }

        notify.send(
            sender=user,
            recipient=recipient,
            verb=verb,
            description=description,
            **extra_data,
        )

    @classmethod
    def work_submitted(cls, contract: Contract):
        """Notify the client submits the work"""
        c_user = contract.client_user
        user = User.objects.get(email=f"notifier@{settings.DOMAIN}")
        verb = _("{} work has been submitted by professional".format(contract.job.title))
        description = _("The professional submitted the work. You can check it out!")
        extra_data = {
            "action": {"url": contract.get_absolute_url(), "title": _("View Contract")}
        }

        notify.send(
            sender=user,
            recipient=c_user,
            verb=verb,
            description=description,
            **extra_data,
        )

    @classmethod
    def work_accepted(cls, contract: Contract):
        """Notify the professional when the work is accepted by client"""
        c_professional = contract.professional_user
        user = User.objects.get(email=f"notifier@{settings.DOMAIN}")
        verb = _("{} work has been accepted by client".format(contract.job.title))
        description = _("The client accepted the work. Congrats!")
        extra_data = {
            "action": {"url": contract.get_absolute_url(), "title": _("View Contract")}
        }

        notify.send(
            sender=user,
            recipient=c_professional,
            verb=verb,
            description=description,
            **extra_data,
        )


class NotificationServiceFactory:
    @staticmethod
    def create_notification_service(notification_type):
        if notification_type == "email":
            return NotificationService(EmailNotificationStrategy())
        elif notification_type == "sms":
            return NotificationService(SMSNotificationStrategy())
        elif notification_type == "push":
            return NotificationService(PushNotificationStrategy())
        else:
            raise ValueError("Invalid notification type")
