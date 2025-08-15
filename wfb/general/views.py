from django.shortcuts import render
from django.utils.translation import get_language
from django.utils.translation import gettext as _

# internals


def contact_us(request):
    context = {"title": _("Contact Us Page")}
    lang = get_language()
    return render(request, f"general/contactus/{lang}.html", context)


def about_us(request):
    context = {"title": _("About Us Page")}
    lang = get_language()
    return render(request, f"general/aboutus/{lang}.html", context)
