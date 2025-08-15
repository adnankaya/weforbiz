from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxLengthValidator
from taggit.managers import TaggableManager
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from slugify import slugify
from ckeditor.fields import RichTextField

# internals
from wfb.core.models import BaseModel
from .managers import PostObjectsManager, CategoryObjectsManager
from wfb.core.models import UrlHit

# globals
User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=32)
    name_en = models.CharField(max_length=32, null=True, blank=True)
    slug = models.SlugField(max_length=250, unique=True)
    icon = models.CharField(max_length=64, null=True, blank=True)

    # actives = CategoryObjectsManager()

    CACHE_KEY = "categories"

    class Meta:
        db_table = "t_category"
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)


class Post(BaseModel):
    """
    Post Model
    """

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    body = RichTextField(validators=[MaxLengthValidator(81920)])
    slug = models.SlugField(max_length=250, unique_for_date="created_date")
    category = models.ForeignKey("Category", on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    tags = TaggableManager()
    actives = PostObjectsManager()

    CACHE_KEY = "post_actives"

    class Meta:
        db_table = "t_post"
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        unique_together = ["created_by", "slug"]

    def __str__(self) -> str:
        return self.title

    def get_tags(self):
        return self.tags.all()

    def get_hit_count(self):
        qs = UrlHit.objects.filter(url=self.get_absolute_url()).first()
        if qs:
            return qs.hits_count
        return 0

    def process_slugify(self):
        if self.created_date:
            _date = self.created_date.strftime("%Y-%m-%d")
        else:
            _date = timezone.datetime.today().strftime("%Y-%m-%d")
        self.slug = f"{slugify(self.title)}-{_date}"

    def save(self, *args, **kwargs):
        try:
            with transaction.atomic():
                self.process_slugify()
                super(Post, self).save(*args, **kwargs)
        except Exception as e:
            raise ValueError(e)

    def get_absolute_url(self):
        return reverse(
            "blog:post-detail",
            args=[
                self.created_date.year,
                self.created_date.month,
                self.created_date.day,
                self.slug,
                self.pk,
            ],
        )


class PostImage(BaseModel):
    post = models.ForeignKey("Post", on_delete=models.CASCADE)
    image = models.ImageField(_("Image"), upload_to="images/posts/")

    class Meta:
        db_table = "t_post_image"
        verbose_name = "Post Image"
        verbose_name_plural = "Post Images"

    def __str__(self) -> str:
        return self.image.path




