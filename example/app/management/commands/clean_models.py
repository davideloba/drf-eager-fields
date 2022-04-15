from django.core.management.base import BaseCommand

from django.core.management.color import no_style
from django.db import connection

from ...models import Customer, Region, Country, CustomerCountry, Article, Order


class Command(BaseCommand):
    help = 'Clea models data.'

    def handle(self, *args, **options):
        target_models = [Customer, Region, Country, CustomerCountry, Article, Order]

        # Delete models data
        for m in target_models:
            res = m.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'[{m.__name__}] removed the following data: {res}'))


        # Rest sequence ids
        self.stdout.write(self.style.SUCCESS(f'Reset of id sequences ...'))
        sequence_sql = connection.ops.sequence_reset_sql(
            no_style(),
            target_models
        )
        with connection.cursor() as cursor:
            for sql in sequence_sql:
                cursor.execute(sql)

