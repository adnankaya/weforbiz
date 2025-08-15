# -*- coding: utf-8 -*-
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from django.apps import apps





class Command(BaseCommand):
    help = 'Generate payment'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(
            "\nProcess started...{}\n").format(__name__))

        try:
            pass
        except Exception as e:
            raise e

        self.stdout.write(self.style.SUCCESS("Process finished"))
