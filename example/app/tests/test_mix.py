import random
import string

from rest_framework.test import APITestCase
from django.urls import reverse

from ..models import Article, Customer, Country, Region, Order


class TestEagerFields(APITestCase):
    fixtures = ['test.yaml']

    def tearDown(self):
        Customer.objects.all().delete()
        Article.objects.all().delete()
        Region.objects.all().delete()

    def test_tnt(self):
        url = reverse('article-detail', kwargs={'pk': 1}) # 1: TNT, see fixtures

        only = 'code'
        res = self.client.get(f'{url}?only_fields=code', format="json")
        self.assertEqual(
            res.data,
            {
                "code": "TNT",
            },
        )

        eager = 'customer'
        only = 'code,customer.name'
        res = self.client.get(f'{url}?eager_fields={eager}&only_fields={only}', format="json")
        self.assertEqual(
            res.data,
            {
                "code": "TNT",
                "customer": {
                    "name": "Willy"
                }
            },
        )

        with self.assertNumQueries(6):
            eager='orders.customer,customer.countries.region'
            only='code,orders.description,orders.customer,customer.name,customer.id,customer.countries.name,customer.countries.region.name'
            exclude='orders.customer.id'
            res = self.client.get(f'{url}?eager_fields={eager}&exclude_fields={exclude}&only_fields={only}', format="json")

            self.assertEqual(
                res.data,
                {
                    "code": "TNT",
                    "orders": [
                        {"description": "beep beep will be mine!", "customer": { "name": "Willy" }},
                        {"description": "beep beep will be mine!", "customer": { "name": "Willy" }},
                        {"description": "beep beep will be mine!", "customer": { "name": "Willy" }},
                        {"description": "beep beep will be mine!", "customer": { "name": "Willy" }},
                        {"description": "beep beep will be mine!", "customer": { "name": "Willy" }},
                        {"description": "beep beep will be mine!", "customer": { "name": "Willy" }},
                        {"description": "beep beep will be mine!", "customer": { "name": "Willy" }},
                        {"description": "beep beep will be mine!", "customer": { "name": "Willy" }},
                        {"description": "beep beep will be mine!", "customer": { "name": "Willy" }},
                        {"description": "beep beep will be mine!", "customer": { "name": "Willy" }},
                    ],
                    "customer": {
                        "id": 1,
                        "name": "Willy",
                        "countries": [
                            {
                                "name": "USA",
                                "region": {
                                    "name": "America"
                                }
                            },
                        ]
                    },
                },
            )
    