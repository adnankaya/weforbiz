from django.db import transaction

from wfb.core.services import CoreService

from .forms import AddressCreateForm
from .models import Country, City, Address


class AddressService(CoreService):
    @classmethod
    def save_address(cls, request, address=None):
        professional = request.user.professional
        client = request.user.client
        if request.method == "POST":
            form = AddressCreateForm(request.POST)
            if form.is_valid():
                with transaction.atomic():
                    country, coc = Country.objects.get_or_create(
                        name=form.cleaned_data["country"]
                    )
                    city, cic = City.objects.get_or_create(
                        name=form.cleaned_data["city"], country=country
                    )
                    qs_address = Address.objects.filter(
                        city=city, line=form.cleaned_data["line"]
                    )
                    address = None
                    if qs_address:
                        address = qs_address.first()
                    else:
                        address = Address.objects.create(
                            city=city, line=form.cleaned_data["line"]
                        )

                    if professional and request.session["is_professional"]:
                        professional.address = address
                        professional.save()
                    elif client and request.session["is_client"]:
                        client.address = address
                        client.save()
                    return True
        return False
