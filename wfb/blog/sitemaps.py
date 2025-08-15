from django.contrib.sitemaps import Sitemap

from .models import Post


class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Post.actives.all()

    def lastmod(self, obj: Post):
        return obj.updated_date
