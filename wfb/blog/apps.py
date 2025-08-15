from django.apps import AppConfig


class PostConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "wfb.blog"

    def ready(self) -> None:
        from . import signals
