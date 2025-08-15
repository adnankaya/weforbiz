import os
import math
from django import template
from django.utils.safestring import mark_safe
from django.db.models.functions import Length
from django.core.cache import cache
from django.utils.timezone import now
from allauth.account.utils import has_verified_email
from datetime import datetime
from datetime import timedelta

# internals
from wfb.core.choices import Duration

register = template.Library()


@register.simple_tag
def get_website():
    from wfb.core.models import Website

    return Website.objects.first()


@register.simple_tag
def is_email_verified(user, email):
    return has_verified_email(user, email)


@register.simple_tag
def render_stars(rating):
    if isinstance(rating, str):
        rating = float(rating)

    # Round to the nearest 0.5
    rounded_rating = round(rating * 2) / 2

    full_stars = math.floor(rounded_rating)
    half_stars = 1 if rounded_rating - full_stars == 0.5 else 0
    empty_stars = 5 - (full_stars + half_stars)

    stars = ""
    for _ in range(full_stars):
        stars += '<i class="fa-solid fa-star"></i>'
    for _ in range(half_stars):
        stars += '<i class="fa-solid fa-star-half-stroke"></i>'
    for _ in range(empty_stars):
        stars += '<i class="fa-regular fa-star"></i>'

    return mark_safe(stars)


@register.filter
def humanize_duration(value):
    return dict(Duration.choices).get(value, value)


@register.simple_tag
def is_online(last_login):
    """if last login is in 30 minutes return True"""
    return last_login > (now() - timedelta(minutes=30))


@register.simple_tag
def get_appname():
    return os.getenv("APP_NAME", "App")


@register.simple_tag
def get_themes():
    return [
        "agate",
        "atom-one-dark",
        "atom-one-light",
        "default",
        "far",
        "felipec",
        "foundation",
        "github-dark",
        "github",
        "kimbie-light",
        "mono-blue",
        "monokai-sublime",
        "night-owl",
        "purebasic",
        "qtcreator-light",
        "school-book",
        "srcery",
        "stackoverflow-dark",
        "stackoverflow-light",
        "vs",
        "vs2015",
        "xt256",
    ]
