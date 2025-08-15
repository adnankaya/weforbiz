# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.db import transaction
import random

from wfb.users.models import User, Professional


first_names = ["Muhammad", "Saladin", "Mehmed", "Suleiman", "Omar", "Khalid", "Tariq", "Abraham","Abdul","Adnan","Hasan"]
last_names = ["Ameen", "Ayyub", "Fatih", "Sultan", "Khattab", "al-Walid", "Ziyad", "Faith","Hameed","Kaya","Benna"]



class Command(BaseCommand):
    help = "Generate professionals"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("\nProcess started...{}\n").format(__name__)
        )

        try:
            with transaction.atomic():
                for i in range(10, 21):
                    phone = random.randint(1000, 9999)
                    user, created_u = User.objects.get_or_create(
                        email=f"profile{i}@example.com",
                    )
                    user.first_name = first_names[i//10]
                    user.last_name = last_names[i//10]
                    user.set_password("qwert")
                    user.email_verified = True
                    user.save()
                    professional, created_f = Professional.objects.get_or_create(
                        profile_type=Professional.Types.FREELANCER,
                        user=user,
                        address=None,
                        phone=f"555555{phone}",
                    )
        except Exception as e:
            raise e

        self.stdout.write(self.style.SUCCESS("Process finished"))
