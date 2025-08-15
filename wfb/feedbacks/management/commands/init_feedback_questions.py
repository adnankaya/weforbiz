# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.db import transaction

from wfb.feedbacks.models import FeedbackQuestion


class Command(BaseCommand):
    help = "Create feedback questions"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                "\nStarted creating FeedbackQuestion objects...{}\n"
            ).format(__name__)
        )
        with transaction.atomic():
            FeedbackQuestion.objects.get_or_create(text="Communication")
            FeedbackQuestion.objects.get_or_create(text="Cooperation")
            FeedbackQuestion.objects.get_or_create(text="Availability")
            FeedbackQuestion.objects.get_or_create(text="Skills")
            FeedbackQuestion.objects.get_or_create(text="Quality of Requirements")

        self.stdout.write(self.style.SUCCESS("Finished"))
