# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.apps import apps
from django.db import transaction
import random

from wfb.users.models import User
from wfb.blog.models import Category, Post

B_TITLES = [
    "Example title for python web development",
    "About Django",
]
B_DESCRIPTIONS = [
    "You can use python, flask for web backend devleopment and angular for frontend.",
    "Django is a nice framework to build web applications",
]

B_TAGS = [
    ["python", "django", "flask", "html", "css"],
    ["python", "django", "html", "javascript"],
]


class Command(BaseCommand):
    help = "Generate posts"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("\nProcess started...{}\n").format(__name__)
        )

        def get_random_category():
            return random.sample(
                list(Category.objects.values_list("id", flat=True)), 1
            )[0]

        def get_random_user():
            return random.sample(list(User.objects.values_list("id", flat=True)), 1)[0]

        try:
            with transaction.atomic():
                for i in range(0, 2):
                    user = get_random_user()
                    post, created = Post.objects.get_or_create(
                        created_by_id=user,
                        title=B_TITLES[i],
                        body=B_DESCRIPTIONS[i],
                        slug=f"",
                        category_id=get_random_category(),
                        is_active=True,
                    )
                    for tag in B_TAGS[i]:
                        post.tags.add(tag)
        except Exception as e:
            raise e

        self.stdout.write(self.style.SUCCESS("Process finished"))
