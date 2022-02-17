from django.db.models.query import Prefetch
from django.utils.functional import classproperty
from drf_eager_fields.serializers import EagerFieldsSerializer
from rest_framework import serializers

from ..models import Customer


class CustomerSerializer(serializers.ModelSerializer, EagerFieldsSerializer):
    class Meta:
        fields = (
            "id",
            "name",
        )
        model = Customer

        @classproperty
        def extra(self):
            from .article_serializer import ArticleSerializer
            from .country_serializer import CountrySerializer

            return {
                "articles": {
                    "field": ArticleSerializer(many=True),
                    "prefetch": True,
                },
                "filtered_articles": {
                    "field": ArticleSerializer(many=True),
                },
                "countries": {
                    "field": CountrySerializer(many=True),
                    "prefetch": Prefetch(
                        "countries", queryset=CountrySerializer.Meta.model.objects.all()
                    ),
                },
            }


class LazyCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            "id",
            "name",
        )
        model = Customer
