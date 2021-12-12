import json
from rest_framework.test import APITestCase
from django.urls import reverse

from ..models import Article, Customer, Country, Region, Order


class TestTNT(APITestCase):

    fixtures = [
        "0010_countries.yaml",
        "0020_customers_articles.yaml",
        "0030_orders.yaml",
    ]
    url = reverse("article-detail", kwargs={"pk": 1})  # 1: TNT, see fixtures

    def tearDown(self):
        Customer.objects.all().delete()
        Article.objects.all().delete()
        Region.objects.all().delete()

    def test_eager_loading(self):
        with self.assertNumQueries(6):
            extra = "last_10_orders.customer,customer.countries.region"
            fields = "code,last_10_orders.description,last_10_orders.customer,customer.name,customer.id,customer.countries.name,customer.countries.region.name"
            exclude = "last_10_orders.customer.id"
            res = self.client.get(
                f"{self.url}?extra={extra}&fields={fields}&exclude={exclude}",
                format="json",
            )

            self.assertEqual(
                res.data,
                {
                    "code": "TNT",
                    "last_10_orders": [
                        {
                            "description": "beep beep will be mine!",
                            "customer": {"name": "Willy"},
                        },
                        {
                            "description": "beep beep will be mine!",
                            "customer": {"name": "Willy"},
                        },
                        {
                            "description": "beep beep will be mine!",
                            "customer": {"name": "Willy"},
                        },
                        {
                            "description": "beep beep will be mine!",
                            "customer": {"name": "Willy"},
                        },
                        {
                            "description": "beep beep will be mine!",
                            "customer": {"name": "Willy"},
                        },
                        {
                            "description": "beep beep will be mine!",
                            "customer": {"name": "Willy"},
                        },
                        {
                            "description": "beep beep will be mine!",
                            "customer": {"name": "Willy"},
                        },
                        {
                            "description": "beep beep will be mine!",
                            "customer": {"name": "Willy"},
                        },
                        {
                            "description": "beep beep will be mine!",
                            "customer": {"name": "Willy"},
                        },
                        {
                            "description": "beep beep will be mine!",
                            "customer": {"name": "Willy"},
                        },
                    ],
                    "customer": {
                        "id": 1,
                        "name": "Willy",
                        "countries": [
                            {"name": "USA", "region": {"name": "America"}},
                        ],
                    },
                },
            )

    def test_fields(self):
        fields = "code"
        res = self.client.get(f"{self.url}?fields={fields}", format="json")
        self.assertEqual(
            res.data,
            {
                "code": "TNT",
            },
        )

    def test_extra_plus_fields(self):
        extra = "customer"
        fields = "code,customer.name"
        res = self.client.get(
            f"{self.url}?extra={extra}&fields={fields}", format="json"
        )
        self.assertEqual(
            res.data,
            {"code": "TNT", "customer": {"name": "Willy"}},
        )

    def test_exclude(self):
        fields = "id, code, customer.id, customer.name"
        res = self.client.get(f"{self.url}?fields={fields}", format="json")
        self.assertEqual(
            res.data,
            {"id": 1, "code": "TNT", "customer": {"id": 1, "name": "Willy"}},
        )

        exclude = "id, customer.id"
        res = self.client.get(
            f"{self.url}?fields={fields}&exclude={exclude}", format="json"
        )
        self.assertEqual(
            res.data,
            {"code": "TNT", "customer": {"name": "Willy"}},
        )
