import json
from rest_framework.test import APITestCase
from django.urls import reverse

from ..models import Article, Customer, Region


class TestBodyFields(APITestCase):

    fixtures = [
        "0010_countries.yaml",
        "0020_customers_articles.yaml",
    ]

    url = reverse("articles-list")

    def tearDown(self):
        Customer.objects.all().delete()
        Article.objects.all().delete()
        Region.objects.all().delete()

    def test_body_fields(self):
        body = {
            "fields": {
                "code": None,
                "customer": {
                    "name": None,
                    "countries": {"name": None, "region": {"countries": None}},
                },
            }
        }

        res = self.client.generic(
            method="GET",
            path=self.url,
            data=json.dumps(body),
            content_type="application/json",
        )
        self.assertEqual(
            res.data,
            [
                {
                    "code": "TNT",
                    "customer": {
                        "name": "Willy",
                        "countries": [
                            {
                                "name": "USA",
                                "region": {"countries": [{"id": 2, "name": "USA"}]},
                            }
                        ],
                    },
                },
                {
                    "code": "PIZZA",
                    "customer": {
                        "name": "Mario",
                        "countries": [
                            {
                                "name": "Italy",
                                "region": {"countries": [{"id": 1, "name": "Italy"}]},
                            },
                            {
                                "name": "USA",
                                "region": {"countries": [{"id": 2, "name": "USA"}]},
                            },
                        ],
                    },
                },
                {
                    "code": "SIGN",
                    "customer": {
                        "name": "Willy",
                        "countries": [
                            {
                                "name": "USA",
                                "region": {"countries": [{"id": 2, "name": "USA"}]},
                            }
                        ],
                    },
                },
            ],
        )
