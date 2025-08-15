from django.db import models
from django.core.cache import cache
from django.apps import apps
#  internals


class CategoryObjectsManager(models.Manager):
    def get_queryset(self):
        Category = apps.get_model("blog", "Category")
        qs = cache.get(key=Category.CACHE_KEY)
        if not qs:
            qs = super().get_queryset()
            qs.order_by("name")
            cache.set(key=Category.CACHE_KEY, value=qs)
        return qs


class PostObjectsManager(models.Manager):
    def get_queryset(self):
        Post = apps.get_model("blog", "Post")
        qs = cache.get(key=Post.CACHE_KEY)
        if not qs:
            qs = super(PostObjectsManager, self).get_queryset()
            qs = qs.filter(
                is_deleted=False,
                is_active=True
            ).select_related(
                "created_by",
                "category"
            ).prefetch_related(
                "tags"
            ).order_by("-created_date")
            cache.set(key=Post.CACHE_KEY, value=qs)
        return qs
