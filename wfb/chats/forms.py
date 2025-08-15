from django import forms

# internals

from wfb.jobs.models import Job
from .models import ChatRoom

class ChatRoomForm(forms.ModelForm):
    job = forms.ModelChoiceField(queryset=Job.objects.all())
    class Meta:
        model = ChatRoom
        fields = [
            "job",
            "room_name",
        ]
