from functools import wraps
from django.urls import reverse

from django.shortcuts import HttpResponseRedirect


def profile_complete_required(func):
    @wraps(func)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            if not (request.user.professional or request.user.client) and request.path != reverse("users:profile-create"):
                return HttpResponseRedirect(reverse("users:profile-create"))
        return func(request, *args, **kwargs)
    return wrap