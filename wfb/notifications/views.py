# -*- coding: utf-8 -*-
""" Django Notifications example views """


from typing import Any
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.utils.encoding import iri_to_uri
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.generic import ListView
from django.apps import apps

from wfb.notifications.helpers import get_notification_list
from wfb.notifications.utils import slug2id
from wfb.notifications.models import Notification

Notification = apps.get_model("notifications", "Notification")

from django.http import JsonResponse  # noqa


class NotificationViewList(ListView):
    template_name = "notifications/list.html"
    context_object_name = "notifications"
    paginate_by = settings.NOTIFICATONS_CONFIG["PAGINATE_BY"]

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(NotificationViewList, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            "notification_types":Notification.Type
        })
        return ctx

class AllNotificationsList(NotificationViewList):
    """
    Index page for authenticated user
    """

    def get_queryset(self):
        if settings.NOTIFICATONS_CONFIG["SOFT_DELETE"]:
            qset = self.request.user.notifications.active()
        else:
            qset = self.request.user.notifications.all()
        return qset


class UnreadNotificationsList(NotificationViewList):
    def get_queryset(self):
        return self.request.user.notifications.unread()


@login_required
def mark_all_as_read(request):
    request.user.notifications.mark_all_as_read()

    _next = request.GET.get("next")

    if _next and url_has_allowed_host_and_scheme(_next, settings.ALLOWED_HOSTS):
        return redirect(iri_to_uri(_next))
    return redirect("notifications:unread")


@login_required
def mark_as_read(request, slug=None):
    notification_id = slug2id(slug)

    notification = get_object_or_404(
        Notification, recipient=request.user, id=notification_id
    )
    notification.mark_as_read()

    _next = request.GET.get("next")

    if _next and url_has_allowed_host_and_scheme(_next, settings.ALLOWED_HOSTS):
        return redirect(iri_to_uri(_next))

    return redirect("notifications:unread")


@login_required
def mark_as_unread(request, slug=None):
    notification_id = slug2id(slug)

    notification = get_object_or_404(
        Notification, recipient=request.user, id=notification_id
    )
    notification.mark_as_unread()

    _next = request.GET.get("next")

    if _next and url_has_allowed_host_and_scheme(_next, settings.ALLOWED_HOSTS):
        return redirect(iri_to_uri(_next))

    return redirect("notifications:unread")


@login_required
def delete(request, slug=None):
    notification_id = slug2id(slug)

    notification = get_object_or_404(
        Notification, recipient=request.user, id=notification_id
    )

    if settings.NOTIFICATONS_CONFIG["SOFT_DELETE"]:
        notification.deleted = True
        notification.save()
    else:
        notification.delete()

    _next = request.GET.get("next")

    if _next and url_has_allowed_host_and_scheme(_next, settings.ALLOWED_HOSTS):
        return redirect(iri_to_uri(_next))

    return redirect("notifications:all")


@never_cache
def live_unread_notification_count(request):
    try:
        user_is_authenticated = request.user.is_authenticated()
    except TypeError:  # Django >= 1.11
        user_is_authenticated = request.user.is_authenticated

    if not user_is_authenticated:
        data = {"unread_count": 0}
    else:
        data = {
            "unread_count": request.user.notifications.unread().count(),
        }
    return JsonResponse(data)


@never_cache
def live_unread_notification_list(request):
    """Return a json with a unread notification list"""
    try:
        user_is_authenticated = request.user.is_authenticated()
    except TypeError:  # Django >= 1.11
        user_is_authenticated = request.user.is_authenticated

    if not user_is_authenticated:
        data = {"unread_count": 0, "unread_list": []}
        return JsonResponse(data)

    unread_list = get_notification_list(request, "unread")

    data = {
        "unread_count": request.user.notifications.unread().count(),
        "unread_list": unread_list,
    }
    return JsonResponse(data)


@never_cache
def live_all_notification_list(request):
    """Return a json with a unread notification list"""
    try:
        user_is_authenticated = request.user.is_authenticated()
    except TypeError:  # Django >= 1.11
        user_is_authenticated = request.user.is_authenticated

    if not user_is_authenticated:
        data = {"all_count": 0, "all_list": []}
        return JsonResponse(data)

    all_list = get_notification_list(request)

    data = {"all_count": request.user.notifications.count(), "all_list": all_list}
    return JsonResponse(data)


def live_all_notification_count(request):
    try:
        user_is_authenticated = request.user.is_authenticated()
    except TypeError:  # Django >= 1.11
        user_is_authenticated = request.user.is_authenticated

    if not user_is_authenticated:
        data = {"all_count": 0}
    else:
        data = {
            "all_count": request.user.notifications.count(),
        }
    return JsonResponse(data)
