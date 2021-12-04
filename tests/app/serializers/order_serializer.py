from django.utils.functional import classproperty
from drf_eager_fields.eager_fields_serializer import EagerFieldsSerializer
from rest_framework import serializers

from ..models import Order


class OrderSerializer(serializers.ModelSerializer, EagerFieldsSerializer):

    class Meta:
        fields = ('code', 'description', 'created_at')
        model = Order
        
        @classproperty
        def eager_fields(self):
            from .customer_serializer import CustomerSerializer
            from .article_serializer import ArticleSerializer
            return {
                'article' : {
                    'field': ArticleSerializer(),
                    'prefetch': True
                },
                'customer': {
                    'field': CustomerSerializer(),
                    'prefetch': True,
                }
            }
