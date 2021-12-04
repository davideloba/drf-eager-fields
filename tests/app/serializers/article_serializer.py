from django.utils.functional import classproperty
from rest_framework import serializers
from drf_eager_fields.eager_fields_serializer import EagerFieldsSerializer

from ..models import Article


class ArticleSerializer(serializers.ModelSerializer, EagerFieldsSerializer):

    class Meta:
        model = Article
        fields = ('code', 'description', )

        @classproperty
        def eager_fields(self):
            from .customer_serializer import CustomerSerializer
            return {
                'customer' : {
                    'field': CustomerSerializer(),
                    'prefetch': True # default queryset=Customer.objects.all() 
                },
                'id': {
                    'field': serializers.IntegerField()
                }
            }

