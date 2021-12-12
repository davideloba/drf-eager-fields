from drf_eager_fields.views import EagerFieldsAPIView
from rest_framework import generics

from .models import Article, Customer
from .serializers.article_serializer import ArticleSerializer, LazyArticleSerializer
from .serializers.customer_serializer import CustomerSerializer


class ArticleList(generics.ListCreateAPIView, EagerFieldsAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    serializer_extra = "order.customer, customer.country"
    # serializer_fields =
    # serializer_exclude =


class ArticleDetail(generics.RetrieveAPIView, EagerFieldsAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    serializer_extra = "order.customer, customer.country"
    # serializer_fields =
    # serializer_exclude_fields =


class LazyArticleList(generics.ListCreateAPIView, EagerFieldsAPIView):
    queryset = Article.objects.all()
    serializer_class = LazyArticleSerializer


class CustomerList(generics.ListCreateAPIView, EagerFieldsAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer()


class CustomerDetail(generics.RetrieveAPIView, EagerFieldsAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer()


class LazyCustomerDetail(generics.RetrieveAPIView, EagerFieldsAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer()
