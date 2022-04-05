from rest_framework.test import APITestCase
from django.urls import reverse

from ..models import Article, Customer


class TestCustomer(APITestCase):

    fixtures = [
        "0010_countries.yaml",
        "0020_customers_articles.yaml",
    ]
    url = reverse("customers-list")

    def tearDown(self):
        Customer.objects.all().delete()
        Article.objects.all().delete()

    def test_description(self):
        with self.assertNumQueries(3):
            return self.client.get(f"{self.url}?extra=description", format="json")
