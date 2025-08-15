import logging
from django.db.models import Count
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.conf import settings
from django.contrib import messages

# internals
from wfb.core.utils import query_debugger
from wfb.core.services import CoreService
from .models import Post, PostImage

User = get_user_model()
db_logger = logging.getLogger('db')


class PostService(CoreService):

    @staticmethod
    def get_similar_posts(post: Post, size=4):
        # list of similar posts
        post_tags_ids = post.tags.values_list('id', flat=True)
        similar_posts = Post.objects.select_related(
            "created_by",
            "category").prefetch_related(
            "tags", "postimage_set").filter(
            is_deleted=False,
            tags__in=post_tags_ids).exclude(id=post.id)
        similar_posts = similar_posts.annotate(
            same_tags=Count('tags')).order_by('-same_tags', '-created_date')[:size]
        return similar_posts

    @staticmethod
    def profile_posts(user: User):
        return Post.objects.filter(
            is_deleted=False,
            created_by=user).select_related(
            "created_by",
        ).prefetch_related(
            "tags"
        ).order_by("-created_date")

    @classmethod
    def activate_user_posts(cls, user):
        try:
            user.post_set.update(is_active=True)
        except Exception as e:
            raise e

    @classmethod
    def create_post_images(cls, request, post):
        images = request.FILES.getlist("images")
        remaining_image_upload = settings.MAX_POST_IMAGES_LEN - post.postimage_set.count()
        if images:
            if len(images) > remaining_image_upload:
                img_max_err_msg = _(
                    f"""
                    Only {remaining_image_upload} images can be uploaded.
                    Images can be maximum {settings.MAX_POST_IMAGES_LEN}.
                    """
                )
                messages.error(request, img_max_err_msg)
                raise ValidationError(img_max_err_msg)
            try:
                for img in images:
                    PostImage.objects.create(post=post, image=img)
                img_success_ms = _("Uploaded images!")
                messages.success(request, img_success_ms)
            except Exception as e:
                img_err_ms = _("Error! images could not be uploaded!")
                messages.error(request, img_err_ms)
                db_logger.exception({
                    "user": request.user,
                    "exception": e
                })
