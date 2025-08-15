from django import template
from wfb.users.models import Professional, Client
from wfb.jobs.models import Job, Contract


register = template.Library()


@register.filter
def is_workstatus_done(contract_set):
    return contract_set.filter(workstatus=Job.Status.DONE)


@register.simple_tag
def is_work_submitable(contract: Contract, professional: Professional):
    """
    returns True if professional job status is in progress
    """
    if contract.workstatus == Job.Status.IN_PROGRESS:
        return contract.job.proposal_set.filter(created_by=professional).exists()
    return False


@register.simple_tag
def is_work_acceptable(contract: Contract):
    """
    returns True if client job status is in review
    """
    if contract.workstatus == Job.Status.IN_REVIEW:
        return True
    return False
