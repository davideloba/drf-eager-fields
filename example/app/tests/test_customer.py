from rest_framework.test import APITestCase
from django.urls import reverse

from ..models import Article, Customer


class TestCustomer(APITestCase):

    fixtures = [
        "0010_countries.yaml",
        "0020_customers_articles.yaml",
    ]
    url = reverse("customer-detail", kwargs={"pk": 1})  # 1: Willy, see fixtures

    def tearDown(self):
        Customer.objects.all().delete()
        Article.objects.all().delete()

    def test_fields(self):
        extra = "filtered_articles"
        fields = "name, filtered_articles.code"
        res = self.client.get(
            f"{self.url}?extra={extra}&fields={fields}", format="json"
        )
        self.assertEqual(
            res.data,
            {
                "name": "Willy",
                "filtered_articles": [
                    {
                        "code": "SIGN",
                    }
                ],
            },
        )
