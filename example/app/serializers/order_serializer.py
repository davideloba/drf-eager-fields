from django.utils.functional import classproperty
from drf_eager_fields.serializers import EagerFieldsSerializer
from rest_framework import serializers

from ..models import Order
from .customer_serializer import CustomerSerializer


class OrderSerializer(serializers.ModelSerializer, EagerFieldsSerializer):
    class Meta:
        fields = ("code", "description", "created_at")
        model = Order

        @classproperty
        def extra(self):
            from .article_serializer import ArticleSerializer
            from .customer_serializer import CustomerSerializer

            return {
                "article": {"field": ArticleSerializer(), "prefetch": True},
                "customer": {
                    "field": CustomerSerializer(),
                    "prefetch": True,
                },
            }


class LazyOrderSerializer(serializers.ModelSerializer):

    customer = CustomerSerializer()

    class Meta:
        fields = ("code", "description", "created_at", "customer")
        model = Order
