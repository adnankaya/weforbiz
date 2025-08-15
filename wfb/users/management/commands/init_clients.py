# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.db import transaction
import random

from wfb.users.models import User, Client

first_names = ["Josef", "Ahmed", "Ismael", "Yahya", "Abubakr", "Osman", "Ali", "Hamza", "Salih", "Zakariyya", "Luqman"]
last_names = ["Kanan", "Yasin", "Heniye", "Sinwar", "Siddiq", "Zinnurayn", "Talib", "Brave", "Eager", "Smart", "Heal"]

class Command(BaseCommand):
    help = "Generate clients"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("\nProcess started...{}\n").format(__name__)
        )

        try:
            with transaction.atomic():
                for i in range(1, 11):
                    phone = random.randint(1000, 9999)
                    user, created_u = User.objects.get_or_create(
                        email=f"profile{i}@example.com",
                    )
                    user.first_name = first_names[i]
                    user.last_name = last_names[i]
                    user.set_password("qwert")
                    user.email_verified = True
                    user.save()
                    client, created_c = Client.objects.get_or_create(
                        profile_type=Client.Types.CLIENT,
                        user=user,
                        address=None,
                        phone=f"555555{phone}",
                    )
        except Exception as e:
            raise e

        self.stdout.write(self.style.SUCCESS("Process finished"))
