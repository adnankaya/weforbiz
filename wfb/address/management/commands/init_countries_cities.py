# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.db import transaction

from wfb.address.models import City, Country

COUNTRY = {"pk": "90", "name": "Türkiye"}

CITIES = [
    {"pk": "01", "name": "Adana"},
    {"pk": "02", "name": "Adıyaman"},
    {"pk": "03", "name": "Afyon"},
    {"pk": "04", "name": "Ağrı"},
    {"pk": "05", "name": "Amasya"},
    {"pk": "06", "name": "Ankara"},
    {"pk": "07", "name": "Antalya"},
    {"pk": "08", "name": "Artvin"},
    {"pk": "09", "name": "Aydın"},
    {"pk": "10", "name": "Balıkesir"},
    {"pk": "11", "name": "Bilecik"},
    {"pk": "12", "name": "Bingöl"},
    {"pk": "13", "name": "Bitlis"},
    {"pk": "14", "name": "Bolu"},
    {"pk": "15", "name": "Burdur"},
    {"pk": "16", "name": "Bursa"},
    {"pk": "17", "name": "Çanakkale"},
    {"pk": "18", "name": "Çankırı"},
    {"pk": "19", "name": "Çorum"},
    {"pk": "20", "name": "Denizli"},
    {"pk": "21", "name": "Diyarbakır"},
    {"pk": "22", "name": "Edirne"},
    {"pk": "23", "name": "Elazığ"},
    {"pk": "24", "name": "Erzincan"},
    {"pk": "25", "name": "Erzurum"},
    {"pk": "26", "name": "Eskişehir"},
    {"pk": "27", "name": "Gaziantep"},
    {"pk": "28", "name": "Giresun"},
    {"pk": "29", "name": "Gümüşhane"},
    {"pk": "30", "name": "Hakkari"},
    {"pk": "31", "name": "Hatay"},
    {"pk": "32", "name": "Isparta"},
    {"pk": "33", "name": "Mersin"},
    {"pk": "34", "name": "İstanbul"},
    {"pk": "35", "name": "İzmir"},
    {"pk": "36", "name": "Kars"},
    {"pk": "37", "name": "Kastamonu"},
    {"pk": "38", "name": "Kayseri"},
    {"pk": "39", "name": "Kırklareli"},
    {"pk": "40", "name": "Kırşehir"},
    {"pk": "41", "name": "Kocaeli"},
    {"pk": "42", "name": "Konya"},
    {"pk": "43", "name": "Kütahya"},
    {"pk": "44", "name": "Malatya"},
    {"pk": "45", "name": "Manisa"},
    {"pk": "46", "name": "Kahramanmaraş"},
    {"pk": "47", "name": "Mardin"},
    {"pk": "48", "name": "Muğla"},
    {"pk": "49", "name": "Muş"},
    {"pk": "50", "name": "Nevşehir"},
    {"pk": "51", "name": "Niğde"},
    {"pk": "52", "name": "Ordu"},
    {"pk": "53", "name": "Rize"},
    {"pk": "54", "name": "Sakarya"},
    {"pk": "55", "name": "Samsun"},
    {"pk": "56", "name": "Siirt"},
    {"pk": "57", "name": "Sinop"},
    {"pk": "58", "name": "Sivas"},
    {"pk": "59", "name": "Tekirdağ"},
    {"pk": "60", "name": "Tokat"},
    {"pk": "61", "name": "Trabzon"},
    {"pk": "62", "name": "Tunceli"},
    {"pk": "63", "name": "Şanlıurfa"},
    {"pk": "64", "name": "Uşak"},
    {"pk": "65", "name": "Van"},
    {"pk": "66", "name": "Yozgat"},
    {"pk": "67", "name": "Zonguldak"},
    {"pk": "68", "name": "Aksaray"},
    {"pk": "69", "name": "Bayburt"},
    {"pk": "70", "name": "Karaman"},
    {"pk": "71", "name": "Kırıkkale"},
    {"pk": "72", "name": "Batman"},
    {"pk": "73", "name": "Şırnak"},
    {"pk": "74", "name": "Bartın"},
    {"pk": "75", "name": "Ardahan"},
    {"pk": "76", "name": "Iğdır"},
    {"pk": "77", "name": "Yalova"},
    {"pk": "78", "name": "Karabük"},
    {"pk": "79", "name": "Kilis"},
    {"pk": "80", "name": "Osmaniye"},
    {"pk": "81", "name": "Düzce"},
]


class Command(BaseCommand):
    help = "Generate addresses"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("\nProcess started...{}\n").format(__name__)
        )
        try:
            with transaction.atomic():
                country, _ = Country.objects.get_or_create(**COUNTRY)
                for city in CITIES:
                    City.objects.get_or_create(country=country, **city)
        except Exception as e:
            raise e

        self.stdout.write(self.style.SUCCESS("Process finished"))
