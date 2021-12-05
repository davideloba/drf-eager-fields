from drf_eager_fields.views import EagerFieldsAPIView
from rest_framework import generics

from .models import Article
from .serializers.article_serializer import ArticleSerializer


class ArticleList(generics.ListCreateAPIView, EagerFieldsAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    serializer_eager_fields = 'order.customer, customer.country'
    # serializer_only_fields = 
    # serializer_exclude_fields = 


class ArticleDetail(generics.RetrieveAPIView, EagerFieldsAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    serializer_eager_fields = 'order.customer, customer.country'
    # serializer_only_fields = 
    # serializer_exclude_fields = 
