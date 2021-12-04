from django.db.models.query import Prefetch
from django.utils.functional import classproperty
from drf_eager_fields.eager_fields_serializer import EagerFieldsSerializer
from rest_framework import serializers

from ..models import Customer


class CustomerSerializer(serializers.ModelSerializer, EagerFieldsSerializer):

    class Meta:
        fields = ('name',)
        model = Customer
        
        @classproperty
        def eager_fields(self):
            from app.serializers.article_serializer import ArticleSerializer
            from app.serializers.country_serializer import CountrySerializer
            return {
                'articles' : {
                    'field': ArticleSerializer(many=True),
                },
                'countries': {
                    'field': CountrySerializer(many=True),
                    'prefetch': Prefetch('countries', queryset=CountrySerializer.Meta.model.objects.all()),
                }
            }

