import celery
from celery.utils.log import get_task_logger
from django.db.models import Q



from wfb.address.models import Address

logger = get_task_logger(__name__)


@celery.shared_task
def delete_unused_addresses_task():
    try:
        qs = Address.objects.exclude(Q(professional__isnull=False) | Q(client__isnull=False))
        qs.delete()
        logger.info("Success on delete_unused_addresses_task")
    except Exception as e:
        logger.exception(f"Error on delete_unused_addresses_task : {e}")
