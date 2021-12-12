from django.db.models.query import Prefetch
from django.utils.functional import classproperty
from drf_eager_fields.serializers import EagerFieldsSerializer
from rest_framework import serializers

from ..models import Region


class RegionSerializer(serializers.ModelSerializer, EagerFieldsSerializer):
    class Meta:
        fields = ("name",)
        model = Region

        @classproperty
        def extra(self):
            from .country_serializer import CountrySerializer

            return {
                "countries": {
                    "field": CountrySerializer(many=True),
                    "prefetch": Prefetch(
                        "countries", queryset=CountrySerializer.Meta.model.objects.all()
                    ),
                }
            }
