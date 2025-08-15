from django.db import models
from django.contrib.auth import get_user_model

# internals
from wfb.core.models import BaseModel

User = get_user_model()


class Country(models.Model):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=8)

    class Meta:
        db_table = "t_country"

    def __str__(self) -> str:
        return self.name


class City(models.Model):
    name = models.CharField(max_length=120)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)

    class Meta:
        db_table = "t_city"

    def __str__(self) -> str:
        return self.name


class Address(BaseModel):
    line = models.TextField()
    city = models.ForeignKey(City, on_delete=models.PROTECT)

    class Meta:
        db_table = "t_address"

    def __str__(self) -> str:
        return f"{self.city.country}-{self.city}-{self.line}"
