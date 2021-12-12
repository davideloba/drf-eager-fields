from django.db.models import Prefetch, Subquery
from django.db.models.expressions import OuterRef
from django.utils.functional import classproperty
from drf_eager_fields.serializers import EagerFieldsSerializer
from rest_framework import serializers

from ..models import Article
from .order_serializer import LazyOrderSerializer


class ArticleSerializer(serializers.ModelSerializer, EagerFieldsSerializer):
    class Meta:
        model = Article
        fields = (
            "id",
            "code",
            "description",
        )

        @classproperty
        def extra(self):
            from .customer_serializer import CustomerSerializer
            from .order_serializer import OrderSerializer

            return {
                "customer": {
                    "field": CustomerSerializer(),
                    "prefetch": True,  # default queryset=Customer.objects.all()
                },
                "orders": {"field": OrderSerializer(many=True), "prefetch": True},
                "last_10_orders": {
                    "field": OrderSerializer(source="orders", many=True),
                    "prefetch": Prefetch(
                        "orders",
                        queryset=OrderSerializer.Meta.model.objects.filter(
                            id__in=Subquery(
                                OrderSerializer.Meta.model.objects.filter(
                                    article_id=OuterRef("article_id")
                                )
                                .order_by("-created_at")
                                .values_list("id", flat=True)[:10]
                            )
                        ).order_by("-created_at"),
                    ),
                },
            }


class LazyArticleSerializer(serializers.ModelSerializer):
    orders = LazyOrderSerializer(many=True)

    class Meta:
        model = Article
        fields = ("id", "code", "description", "orders")
