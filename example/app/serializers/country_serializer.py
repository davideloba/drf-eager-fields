from django.db.models.query import Prefetch
from django.utils.functional import classproperty
from rest_framework import serializers
from drf_eager_fields.serializers import EagerFieldsSerializer

from ..serializers.customer_serializer import LazyCustomerSerializer

from ..models import Country


class CountrySerializer(serializers.ModelSerializer, EagerFieldsSerializer):
    class Meta:
        fields = ("id", "name")
        model = Country

        @classproperty
        def extra(self):
            from .customer_serializer import CustomerSerializer
            from .region_serializer import RegionSerializer

            return {
                "customers": {
                    "field": CustomerSerializer(many=True),
                    "prefetch": Prefetch(
                        "customers",
                        queryset=CustomerSerializer.Meta.model.objects.all(),
                    ),
                },
                "region": {
                    "field": RegionSerializer(),
                    "prefetch": Prefetch("region", queryset=RegionSerializer.Meta.model.objects.all()),
                },
            }


class MixedCountrySerializer(serializers.ModelSerializer, EagerFieldsSerializer):
    """EagerFieldsSerializer without the 'extra' field, for testing purposes"""

    customers = LazyCustomerSerializer(many=True)

    class Meta:
        fields = ("id", "name", "customers")
        model = Country
