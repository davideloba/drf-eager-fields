import json
from django.db import connection, reset_queries
from django.test.utils import CaptureQueriesContext
from rest_framework import settings
from rest_framework.test import APITestCase
from django.urls import reverse

from ..models import Article, Customer, Region


class TestSpeed(APITestCase):

    fixtures = [
        "0010_countries.yaml",
        "0020_customers_articles.yaml",
        "0030_orders.yaml",
    ]

    def tearDown(self):
        Customer.objects.all().delete()
        Article.objects.all().delete()
        Region.objects.all().delete()

    def test_article(self):
        """
        eager loading get the same result
        with 2 orders of magnitude lesser than
        the lazy one
        """
        lazy_url = reverse("lazy-articles-list")

        with CaptureQueriesContext(connection):
            reset_queries()
            lazy_res = self.client.get(
                lazy_url,
                format="json",
            )
            lazy_queries = len(connection.queries)

        eager_url = reverse("articles-list")

        with CaptureQueriesContext(connection):
            reset_queries()
            eager_res = self.client.get(
                f"{eager_url}?extra=orders.customer", format="json"
            )
            eager_queries = len(connection.queries)

        self.assertEqual(lazy_res.data, eager_res.data)
        self.assertGreater(lazy_queries, eager_queries * 100)
