from django.utils.safestring import mark_safe
from django import template
from django.db.models import Count
from taggit.models import Tag
from django.conf import settings
# internals
from wfb.blog.models import Post

register = template.Library()


# TODO
@register.simple_tag
def get_most_viewed_posts():
    return Post.objects.all()

@register.simple_tag
def get_most_used_tags():
    return Tag.objects.annotate(
        num_posts=Count("post")).order_by("-num_posts").values(
        "name", "slug", "num_posts")[:settings.COUNT_MOST_USED_TAGS]
