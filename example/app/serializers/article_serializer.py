from django.utils.functional import classproperty
from rest_framework import serializers
from drf_eager_fields.eager_fields_serializer import EagerFieldsSerializer

from ..models import Article


class ArticleSerializer(serializers.ModelSerializer, EagerFieldsSerializer):

    class Meta:
        model = Article
        fields = ('id', 'code', 'description', )

        @classproperty
        def eager_fields(self):
            from .customer_serializer import CustomerSerializer
            from .order_serializer import OrderSerializer
            return {
                'customer' : {
                    'field': CustomerSerializer(),
                    'prefetch': True # default queryset=Customer.objects.all() 
                },
                'orders': {
                    'field': OrderSerializer(many=True),
                    'prefetch': True
                }
            }

