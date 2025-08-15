from django.shortcuts import render
from django.db import transaction
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
from django.db.models import OuterRef, Exists, Q

# internals
from .models import Address, Country, City
from .services import AddressService

@login_required
def address_detail(request, aid: str):
    address = Address.objects.get(pk=aid)
    context = {"title": "Address Detail", "address": address}
    if request.user.professional and request.session["is_professional"]:
        template_prefix = "professional"
    elif request.user.client and request.session["is_client"]:
        template_prefix = "client"
    return render(request, f"{template_prefix}/detail.html", context)


@login_required
def address_create(request):
    context = {"title": "Address Create"}
    professional = request.user.professional
    client = request.user.client
    if AddressService.save_address(request):
        messages.success(request, _("Created address successfully."))
        return HttpResponseRedirect(reverse("users:settings-contact-info"))
    if professional and request.session["is_professional"]:
        template_prefix = "professional"
    elif client and request.session["is_client"]:
        template_prefix = "client"
    return render(request, f"{template_prefix}/create.html", context)


@login_required
def address_update(request, aid: str):
    address = Address.objects.get(pk=aid)
    context = {"title": "Address Update"}
    if AddressService.save_address(request, address):
        messages.success(request, _("Updated address successfully."))
        return HttpResponseRedirect(reverse("users:settings-contact-info"))
    if request.user.professional and request.session["is_professional"]:
        template_prefix = "professional"
    elif request.user.client and request.session["is_client"]:
        template_prefix = "client"
    return render(request, f"{template_prefix}/update.html", context)
