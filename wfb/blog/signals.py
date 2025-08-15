from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.conf import settings
# internals
from wfb.blog import models as post_models


@receiver(post_save, sender=post_models.Post)
def clear_cache_post_actives(**kwargs):
    cache.delete(key=post_models.Post.CACHE_KEY)

@receiver(post_save, sender=post_models.Category)
def clear_cache_categories(**kwargs):
    cache.delete(key=post_models.Category.CACHE_KEY)


@receiver(post_save, sender=post_models.Post)
def clear_cache_post_index(**kwargs):
    cache.delete(key=settings.KEY_PREFIX_POST_INDEX)




@receiver(post_save, sender=post_models.Post)
@receiver(post_save, sender=post_models.PostImage)
def clear_cache_post_detail(sender, instance, created, **kwargs):
    key = f"{settings.KEY_PREFIX_POST_DETAIL}"
    cache.delete(key=key)
