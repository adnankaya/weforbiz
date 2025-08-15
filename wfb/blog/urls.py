from django.urls import path

from . import views

app_name = "blog"


urlpatterns = [
    path("posts/", views.index, name="index"),
    path(
        "posts/<int:year>/<int:month>/<int:day>/<slug:slug>/<int:pk>/",
        views.detail,
        name="post-detail",
    ),
    # must be end of the urlpatterns
    path("posts/<slug:tag_slug>/", views.index, name="posts-by-tag"),
]
