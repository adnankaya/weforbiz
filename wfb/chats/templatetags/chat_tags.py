from django import template
from wfb.users.models import Professional, Client


register = template.Library()


@register.simple_tag
def get_sender_receiver(request, client, professional):
    if request.user == client.user:
        sender = client
        receiver = professional
    else:
        sender = professional
        receiver = client
    return {"sender": sender, "receiver": receiver}
