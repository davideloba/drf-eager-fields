import random
import string

from rest_framework.test import APITestCase
from django.urls import reverse

from ..models import Article, Customer, Country, Region, Order


class TestEagerFields(APITestCase):
    """
    Test eager loading
    """

    def setUp(self):
        self.willy = Customer.objects.create(name='Willy')
        self.mario = Customer.objects.create(name='Mario')

        self.tnt = Article.objects.create(code='TNT', customer=self.willy)
        self.pizza = Article.objects.create(code='PIZZA', customer=self.mario)

        self.europe=Region.objects.create(name='Europe')
        self.america=Region.objects.create(name='America')

        self.usa = Country.objects.create(name='USA', region=self.america)
        self.italy = Country.objects.create(name='Italy', region=self.europe)

        self.usa.customers.add(self.willy)
        self.usa.customers.add(self.mario)
        self.italy.customers.add(self.mario)

        letters = string.ascii_lowercase

        self.willy_orders = list()
        for x in range(10):
            code = ''.join(random.choice(letters) for i in range(5))
            o = Order.objects.create(code=code, description='beep beep will be mine!', customer=self.willy, article=self.tnt)
            self.willy_orders.append(o)

        self.mario_orders = list()
        for x in range(5):
            code = ''.join(random.choice(letters) for i in range(5))
            o = Order.objects.create(code=code, description='very hungry bro..please hurry up!', customer=self.mario, article=self.pizza)
            self.mario_orders.append(o)

    def tearDown(self):
        Customer.objects.all().delete()
        Article.objects.all().delete()
        Region.objects.all().delete()

    def test_tnt(self):
        url = reverse('article-detail', kwargs={'pk': self.tnt.id})

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
    