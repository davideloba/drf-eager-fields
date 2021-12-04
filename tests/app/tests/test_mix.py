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

        self.willy_order = Order.objects.create(code='YUIOP', description='beep beep will be mine!', customer=self.willy, article=self.tnt)
        self.mario_order = Order.objects.create(code='ZXCVB', description='very hungry bro..please hurry up!', customer=self.mario, article=self.pizza)

    def tearDown(self):
        Customer.objects.all().delete()
        Article.objects.all().delete()
        Region.objects.all().delete()

    def test_tnt(self):
        url = reverse('article-detail', kwargs={'pk': self.tnt.id})

        res = self.client.get(f'{url}?only_fields=code', format="json")
        self.assertEqual(
            res.data,
            {
                "code": "TNT",
            },
        )

        res = self.client.get(f'{url}?eager_fields=customer&only_fields=code,customer.name', format="json")
        self.assertEqual(
            res.data,
            {
                "code": "TNT",
                "customer": {
                    "name": "Willy"
                }
            },
        )

        with self.assertNumQueries(4):
            eager = 'orders.customer,customer.countries.region'
            exclude = 'description,customer.countries.id'
            res = self.client.get(f'{url}?eager_fields={eager}&exclude_fields={exclude}', format="json")
            self.assertEqual(
                res.data,
                {
                    "code": "TNT",
                    "customer": {
                        "name": "Willy",
                        "countries": [
                            {
                                "name": "USA",
                                "region": {
                                    "name": "America"
                                }
                            },
                        ]
                    }
                },
            )
    