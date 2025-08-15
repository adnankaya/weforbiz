from django.db.models.signals import post_save, post_delete
from django.utils.translation import gettext as _
from django.dispatch import receiver
from django.core.cache import cache
from django.conf import settings

# internals
from wfb.jobs.models import Contract, Job, Proposal
from wfb.jobs.enums import BadgesEnum
from wfb.users.models import Professional, User
from wfb.notifications.signals import notify


@receiver(post_save, sender=Contract)
def on_contract_update(sender, instance: Contract, created, **kwargs):
    
    professional = instance.proposal.created_by
    contracts_done = Contract.objects.filter(
        proposal__created_by=professional, workstatus=Job.Status.DONE
    )
    cdc = contracts_done.count()
    if cdc == BadgesEnum.RISING_STAR_NUMBER.value:
        professional.badge = Professional.Badges.RISING_STAR
    if cdc == BadgesEnum.TALENTED_NUMBER.value:
        professional.badge = Professional.Badges.TALENTED
    if cdc == BadgesEnum.EXPERT_NUMBER.value:
        professional.badge = Professional.Badges.EXPERT
    if cdc == BadgesEnum.MASTER_NUMBER.value:
        professional.badge = Professional.Badges.MASTER
    if cdc == BadgesEnum.ELITE_NUMBER.value:
        professional.badge = Professional.Badges.ELITE

    professional.save()
