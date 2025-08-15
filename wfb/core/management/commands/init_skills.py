# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.db import transaction


from wfb.core.models import Skill
from wfb.users.models import User


SKILLS = [
    "html",
    "css",
    "javascript",
    "django",
    "flask",
    "fastapi",
    "python",
    "tensorflow",
    "pytorch",
    "python",
    "c++",
    "c",
    "java",
    "swift",
    "flutter",
    "react native",
]


class Command(BaseCommand):
    help = "Generate skill"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("\nProcess started...{}\n").format(__name__)
        )

        try:
            with transaction.atomic():
                for skill_name in SKILLS:
                    try:
                        sobj = Skill.objects.get(name=skill_name)
                    except Skill.DoesNotExist:
                        sobj = Skill.objects.create(name=skill_name)
        except Exception as e:
            raise e

        self.stdout.write(self.style.SUCCESS("Process finished"))
