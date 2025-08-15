import logging
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.utils.translation import gettext as _
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views.generic import (
    CreateView,
)
from django.views.decorators.vary import vary_on_cookie
from django.views.decorators.cache import cache_page
from django.db import transaction
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from taggit.models import Tag

# internals
from .models import Post, Category, PostImage
from .forms import PostForm, PostSearchForm
from wfb.core.pagination import paginate_objects
from .services import PostService
from wfb.core.services import hit_count_service

# db_logger = logging.getLogger("db")


def index(request, tag_slug=None):
    """
    Users can list post
    """
    all_posts = Post.actives.all()
    categories = Category.objects.all()
    ctx = {}
    category_ids = request.GET.getlist("cid")
    if category_ids:
        all_posts = all_posts.filter(category_id__in=category_ids)
    if "query" in request.GET:
        form = PostSearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data["query"]
            all_posts = all_posts.filter(
                Q(title__icontains=query) | Q(body__icontains=query)
            )
            ctx.update(
                {
                    "query": query,
                }
            )
    # filtering by clicked tag
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        all_posts = all_posts.filter(tags__in=[tag])
    page = request.GET.get("page")
    limit = request.GET.get("limit", settings.POST_LIMIT_PER_PAGE)
    paginated_posts = paginate_objects(all_posts, page, per_page=limit)

    ctx.update(
        {
            "paginated_posts": paginated_posts,
            "page": page,
            "tag": tag,
            "categories": categories,
        }
    )
    return render(request, "blog/index.html", ctx)


def detail(request, year, month, day, slug, pk):
    ctx = {}
    try:
        post = (
            Post.objects.filter(is_deleted=False)
            .select_related("created_by", "category")
            .prefetch_related("tags", "postimage_set")
            .get(pk=pk)
        )
    except Post.DoesNotExist:
        post = None
        messages.error(request, _("Could not found the post!"))
    else:
        ctx.update(
            {
                "post": post,
                "title": post.title,
                "remaining_image_upload": settings.MAX_POST_IMAGES_LEN
                - post.postimage_set.count(),
                "total_image_upload": settings.MAX_POST_IMAGES_LEN,
                "similar_posts": PostService.get_similar_posts(post, 6),
            }
        )
        #  to count views
        hit_count = hit_count_service(request)
        ctx.update({"hit_count": hit_count})
    return render(request, "blog/detail.html", ctx)


