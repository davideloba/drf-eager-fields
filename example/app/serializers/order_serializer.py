from django.utils.functional import classproperty
from drf_eager_fields.serializers import EagerFieldsSerializer
from rest_framework import serializers

from ..models import Order


class OrderSerializer(serializers.ModelSerializer, EagerFieldsSerializer):

    class Meta:
        fields = ('code', 'description', 'created_at')
        model = Order
        
        @classproperty
        def eager_fields(self):
            from .article_serializer import ArticleSerializer
            from .customer_serializer import CustomerSerializer
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
