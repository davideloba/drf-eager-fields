from django.utils.functional import classproperty
from rest_framework import serializers
from drf_eager_fields.serializers import EagerFieldsSerializerMixin

from .article_serializer import ArticleSerializer
from .country_serializer import CountrySerializer
from .order_serializer import OrderSerializer

"""
* articles # data serializer
    ...
    - orders # model serializer, standard field
    - customer # data serializer, extra field
        - countries # model serializer
            - region # model serializer
    - last_10_orders # model serializer, extra
"""


class DataArticleSerializer(EagerFieldsSerializerMixin, serializers.Serializer):
    id = serializers.IntegerField()
    code = serializers.CharField()
    description = serializers.CharField()
    orders = OrderSerializer(many=True)

    class Meta(ArticleSerializer.Meta):
        fields = ("id", "code", "description", "orders")

        @classproperty
        def extra(self):
            extra = ArticleSerializer.Meta.extra
            del extra["orders"]
            del extra["customer"]
            extra["customer"] = {
                "field": DataCustomerSerializer(),
            }

            return extra


class DataCustomerSerializer(serializers.Serializer, EagerFieldsSerializerMixin):

    id = serializers.IntegerField()
    name = serializers.CharField()
    countries = CountrySerializer(many=True)
