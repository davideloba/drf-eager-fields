from django.utils import timezone
from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=20)

    @property
    def filtered_articles(self):
        """Make a custom filter"""
        return self.articles.filter(code__startswith="S")

    @property
    def description(self):
        return "My name is {}, my countries are {} and my articles are {}".format(
            self.name,
            "{},".format(country.name for country in self.countries.all()),
            "{},".format(articles.name for articles in self.articles.all()),
        )


class Region(models.Model):
    name = models.CharField(max_length=20)


class Country(models.Model):
    name = models.CharField(max_length=20)
    customers = models.ManyToManyField(Customer, through="CustomerCountry", related_name="countries")
    region = models.ForeignKey(Region, related_name="countries", on_delete=models.CASCADE)


class CustomerCountry(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)


class Article(models.Model):
    code = models.CharField(max_length=5, unique=True)
    description = models.CharField(max_length=50, null=True)
    customer = models.ForeignKey(Customer, related_name="articles", on_delete=models.CASCADE)


class Order(models.Model):
    code = models.CharField(max_length=5, unique=True)
    description = models.CharField(max_length=50)
    created_at = models.DateTimeField(default=timezone.now)
    article = models.ForeignKey(Article, related_name="orders", on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, related_name="orders", on_delete=models.CASCADE)
