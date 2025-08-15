# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.management.base import BaseCommand

from wfb.users.models import User


class Command(BaseCommand):
    help = "Generate system users"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("\nProcess started...{}\n{}\n").format(
                __name__, self.help
            )
        )
        domain = settings.DOMAIN
        user, created = User.objects.get_or_create(email = f"notifier@{domain}")
        user.email_verified = True
        user.set_password(settings.SYSTEM_USER_PASSWORD)
        user.save()
        self.stdout.write(self.style.SUCCESS("Process finished"))
