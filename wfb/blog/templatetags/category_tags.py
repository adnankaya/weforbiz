from django import template
from django.db.models.functions import Length
from django.core.cache import cache
# internals
from wfb.blog.models import Category

register = template.Library()


@register.simple_tag
def get_categories():
    key = "categories_"
    qs = cache.get(key)
    if not qs:
        qs = Category.objects.annotate(
            len_name=Length("name")).order_by("len_name")
        cache.set(key, value=qs)
    return qs
