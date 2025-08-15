# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.apps import apps
from django.db import transaction
import random
from decimal import Decimal
from wfb.users.models import User, Client
from wfb.jobs.models import Job
from wfb.core.models import Skill


class Command(BaseCommand):
    help = "Generate jobs"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("\nProcess started...{}\n").format(__name__)
        )

        def get_random_skills():
            # Get all skills and shuffle them
            all_skills = Skill.objects.all()
            shuffled_skills = random.sample(list(all_skills), len(all_skills))
            return shuffled_skills

        def get_random_client():
            return random.sample(list(Client.objects.values_list("id", flat=True)), 1)[
                0
            ]

        try:
            with transaction.atomic():
                for _ in range(100):
                    title = f"Demo Job {_ + 1}"
                    description = f"This is a demo job #{_ + 1} description."

                    rand_min = round(Decimal(random.uniform(0, 100)), 2)
                    rand_max = round(Decimal(random.uniform(100, 999)), 2)
                    min_budget = rand_min
                    max_budget = rand_min + rand_max

                    job_type = random.choice([Job.Type.FIXED, Job.Type.HOURLY])
                    client = get_random_client()

                    job = Job.objects.create(
                        title=title,
                        description=description,
                        min_budget=min_budget,
                        max_budget=max_budget,
                        job_type=job_type,
                        created_by_id=client,
                    )

                    # Add random skills to the job
                    skills_count = random.randint(1, 5)
                    selected_skills = get_random_skills()[:skills_count]
                    job.skills.set(selected_skills)

                    # Save the job
                    job.save()

        except Exception as e:
            raise e

        self.stdout.write(self.style.SUCCESS("Process finished"))
