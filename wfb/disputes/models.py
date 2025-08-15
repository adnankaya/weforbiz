from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.core.validators import DecimalValidator
from decimal import Decimal

# internals
from wfb.core.models import Base
from wfb.core.mixins import AttachmentMixin
from wfb.core.choices import ExperienceLevel, Duration
#  constants
User = get_user_model()

class Dispute(Base, AttachmentMixin):
    class DisputeStatus(models.TextChoices):
        OPEN = "OPEN", _("OPEN")
        RESOLVED = "RESOLVED", _("RESOLVED")
        CLOSED = "CLOSED", _("CLOSED")
    status = models.CharField(choices=DisputeStatus.choices, max_length=10,
                              default=DisputeStatus.OPEN)

    job = models.ForeignKey("jobs.Job", on_delete=models.PROTECT)
    reason = models.TextField()
    attachments = models.FileField(upload_to='dispute_attachments', null=True, blank=True)
    
    class Meta:
        db_table = "t_dispute"
    
    
class Resolution(Base):
    dispute = models.ForeignKey(Dispute, on_delete=models.CASCADE)
    description = models.TextField()
    
    class Meta:
        db_table = "t_resolution"

class DisputeMessage(models.Model, AttachmentMixin):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="dispute_messages_sent")
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="dispute_messages_received")
    dispute = models.ForeignKey(Dispute, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    messaged_date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    attachments = models.FileField(upload_to='dispute_message_attachments', null=True, blank=True)

    class Meta:
        db_table = "t_dispute_message"

    @property
    def attachment_url(self):
        if self.attachment:
            return self.attachment.url

    @property
    def attachment_storage_backend(self):
        return settings.DEFAULT_FILE_STORAGE