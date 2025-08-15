import uuid
from django.db import models


class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        abstract = True
class BaseUuidModel(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Skill(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self) -> str:
        return self.name


class UrlHit(models.Model):
    url = models.URLField()
    hits_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "t_urlhit"

    def __str__(self):
        return f"{self.hits_count} | {str(self.url)}"

    def increase(self):
        self.hits_count += 1
        self.save()


class HitCount(models.Model):
    url_hit = models.ForeignKey(UrlHit, editable=False, on_delete=models.CASCADE)
    ip = models.CharField(max_length=40)
    session = models.CharField(max_length=40)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "t_hitcount"


class Website(BaseModel):
    name = models.CharField(max_length=60, unique=True)
    en_meta_description = models.TextField()
    en_meta_keywords = models.TextField()
    tr_meta_description = models.TextField()
    tr_meta_keywords = models.TextField()

    class Meta:
        db_table = "t_website"
        verbose_name = "Website"
        verbose_name_plural = "Websites"

    def __str__(self) -> str:
        return self.name


class Waitlist(BaseModel):
    email = models.EmailField(max_length=64, unique=True)

    class Meta:
        db_table = "t_waitlist"

    def __str__(self) -> str:
        return self.email
