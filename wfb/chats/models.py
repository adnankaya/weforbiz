from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
# internals
from wfb.core.mixins import AttachmentMixin

#  constants
User = get_user_model()


class ChatRoom(models.Model):
    class ChatRoomStatus(models.TextChoices):
        OPEN = "OPEN", _("OPEN")
        CLOSED = "CLOSED", _("CLOSED")
    
    professional = models.ForeignKey("users.Professional", on_delete=models.CASCADE, related_name="professional_chatrooms")
    client = models.ForeignKey("users.Client", on_delete=models.CASCADE, related_name="client_chatrooms")

    job = models.ForeignKey("jobs.Job", on_delete=models.CASCADE)
    
    created_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(_("Status"), max_length=6,
                              choices=ChatRoomStatus.choices, default=ChatRoomStatus.OPEN)
    
    room_name = models.CharField(max_length=256, unique=True)

    class Meta:
        db_table = "t_chat_room"
    
    def __str__(self) -> str:
        return self.room_name


class Message(models.Model, AttachmentMixin):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="messages_sent")
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="messages_received")
    job = models.ForeignKey("jobs.Job", on_delete=models.CASCADE)
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    messaged_date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    attachments = models.FileField(upload_to='message_attachments', null=True, blank=True)

    class Meta:
        db_table = "t_message"

    