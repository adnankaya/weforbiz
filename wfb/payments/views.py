from django.shortcuts import render, redirect
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
from django.views import View
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


import logging
import json



from wfb.payments.models import PaymentMethod
from wfb.payments.services import PaymentService
from wfb.payments.services import PaymentStrategyFactory as Factory


logger = logging.getLogger(__name__)


@login_required
def add_payment_method(request):
    pass


@login_required
def create_submerchant(request):
    if request.method == "POST":
        strategy = Factory.get_strategy(PaymentMethod.IYZICO.value)
        payload = {
            "locale": "tr",
            "conversationId": "987654321",
            "subMerchantExternalId": "B49224",
            "subMerchantType": "PERSONAL",
            "address": "Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1",
            "contactName": "John",
            "contactSurname": "Doe",
            "email": "email@submerchantemail.com",
            "gsmNumber": "+905350000000",
            "name": "John's market",
            "iban": "TR180006200119000006672315",
            "identityNumber": "31300864726",
            "currency": "TRY",
        }
        res = PaymentService(strategy).create_submerchant(payload)

        breakpoint()
        return HttpResponseRedirect(reverse("users:settings-get-paid"))


def index(request):
    ctx = {"title": "payment index"}
    return render(request, "payments/index.html", ctx)


class CheckoutFormInitView(View):
    def post(self, request, *args, **kwargs):
        """If this view requested with POST then we will redirect to paymentPageUrl which is iyzico,
        then payment process will continue there.
        """
        try:
            strategy = Factory.get_strategy(PaymentMethod.IYZICO.value)
            res = PaymentService(strategy).checkout_init()
            return redirect(res["payment_url"])
        except CheckoutFormInitializeException as e:
            logger.exception(e)

    def get(self, request, *args, **kwargs):
        ctx = {"title": _("Checkout Page")}
        strategy = Factory.get_strategy(PaymentMethod.IYZICO.value)
        res = PaymentService(strategy).checkout_init()
        ctx.update(
            {
                "checkout_form_content": res["checkout_form_content"],
            }
        )
        return render(request, "payments/checkout.html", ctx)


@require_POST
@csrf_exempt
def callback(request):
    """The payment service will request to this view"""
    try:
        token = request.POST.get("token")
        strategy = Factory.get_strategy(PaymentMethod.IYZICO.value)
        response = PaymentService(strategy).checkout_retrieve(token)
        return HttpResponseRedirect(response["url"])
    except CheckoutFormRetrieveExeption as e:
        print("callback():::", e)
        logger.exception(e)


class SuccessView(TemplateView):
    template_name = "payments/payment-success.html"


class FailedView(TemplateView):
    template_name = "payments/payment-failed.html"
