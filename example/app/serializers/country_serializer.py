from django.db.models.query import Prefetch
from django.utils.functional import classproperty
from drf_eager_fields.serializers import EagerFieldsSerializer
from rest_framework import serializers

from ..models import Country


class CountrySerializer(serializers.ModelSerializer, EagerFieldsSerializer):

    class Meta:
        fields = ('id', 'name')
        model = Country

        @classproperty
        def eager_fields(self):
            from app.serializers.customer_serializer import CustomerSerializer
            from app.serializers.region_serializer import RegionSerializer
            return {
                'customers' : {
                    'field': CustomerSerializer(many=True),
                    'prefetch': Prefetch('customers', queryset=CustomerSerializer.Meta.model.objects.all()),
                },
                'region': {
                    'field': RegionSerializer(),
                    'prefetch': Prefetch('region', queryset=RegionSerializer.Meta.model.objects.all()),
                }
            }
