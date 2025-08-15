# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.sites.models import Site
from django.conf import settings

from wfb.core.models import Website

en_meta_description = """Professional Marketplace"""
en_meta_keywords = """professional,freelancer,marketplace"""
tr_meta_description = """Profesyonel Pazaryeri, Freelance Çalışma"""
tr_meta_keywords = """profesyonel,yazılımcı,grafiker,tasarımcı,çalışan,usta,uzman"""


class Command(BaseCommand):
    help = "init website"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("\n{} Process started...{}\n").format(
                self.help, __name__
            )
        )

        try:
            with transaction.atomic():
                website, created = Website.objects.get_or_create(
                    name="wfb",
                    en_meta_description=en_meta_description,
                    en_meta_keywords=en_meta_keywords,
                    tr_meta_description=tr_meta_description,
                    tr_meta_keywords=tr_meta_keywords,
                )

                self.stdout.write(self.style.SUCCESS("... Updating Site default object ..."))
                site = Site.objects.get(pk=1)
                if settings.DEBUG:
                    site.domain = "localhost:8000"
                    site.name = "Localhost wfb"
                else:
                    site.domain = "weforbiz.com"
                    site.name = "wfb"
                site.save()

        except Exception as e:
            raise e

        self.stdout.write(self.style.SUCCESS("Process finished"))
