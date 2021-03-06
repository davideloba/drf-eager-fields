from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from ..models import Article, Customer, Region


class TestMixed(APITestCase):

    fixtures = [
        "0010_countries.yaml",
        "0020_customers_articles.yaml",
    ]

    def tearDown(self):
        Customer.objects.all().delete()
        Article.objects.all().delete()
        Region.objects.all().delete()

    def test_mixed_serializers(self):

        res = self.client.generic(method="GET", path=reverse("data-articles"), content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_missing_extra(self):
        res = self.client.generic(method="GET", path=reverse("mixed-countries-list"), content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
