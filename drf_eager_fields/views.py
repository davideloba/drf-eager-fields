from django.db.models import query
from django.db.models.query import Prefetch
from rest_framework.generics import GenericAPIView

from .serializers import (
    EagerFieldsSerializer,
    EagerFieldsSerializerMixin,
    is_many_serializer,
    is_model_serializer,
    is_serializer,
)


class EagerFieldsViewMixin(object):
    def get_serializer_context(self):
        """
        Add our custom fields to the serializer context.
        If the fields keywords [extra, fields, exclude]
        are found in query args take those,
        otherwise use the parameters set in the view.
        In GET request, search for 'fields' dict in body
        and save it in the serializer context,
        overriding the view and query 'fields' params.
        """
        context = super().get_serializer_context()

        for x in ["extra", "fields", "exclude"]:
            params = self.request.query_params.get(x, "")
            if params:
                context[x] = params
            elif hasattr(self, "serializer_" + x):
                context[x] = getattr(self, "serializer_" + x)
        if (
            self.request.method == "GET"
            and self.request.data
            and self.request.data.get("fields", None)
        ):
            context["body_fields"] = self.request.data["fields"]
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        serializer = self.get_serializer()
        if not isinstance(serializer, EagerFieldsSerializer) and not isinstance(
            serializer,
            EagerFieldsSerializerMixin,
        ):
            return queryset
        return self._prefetch_queryset(serializer, queryset)

    def _prefetch_queryset(self, serializer, cur_queryset):
        """
        This will work only for model serializers.
        This will not work if the root serializer is not a model one
        and it will stop at the end of the model serializers chain
        """

        fields = self._pluck(serializer, "fields")

        for k in fields.keys():
            field = fields[k]
            if is_serializer(field):
                if is_model_serializer(serializer) and is_model_serializer(
                    self._pluck(field)
                ):
                    source = field.source if field.source else k
                    relation = self._pluck(serializer, "Meta").model._meta.get_field(
                        source
                    )

                    if relation.is_relation:
                        eager_field = self._pluck(
                            self._pluck(serializer).Meta, "extra"
                        ).get(k, None)
                        prefetch = (
                            eager_field.get("prefetch", None) if eager_field else None
                        )

                        if prefetch and isinstance(prefetch, bool):
                            prefetch = Prefetch(
                                relation.name,
                                queryset=self._pluck(field, "Meta").model.objects.all(),
                            )

                        if prefetch and isinstance(prefetch, Prefetch):
                            cur_queryset = cur_queryset.prefetch_related(
                                Prefetch(
                                    relation.name,
                                    queryset=self._prefetch_queryset(
                                        field, prefetch.queryset
                                    ),
                                )
                            )
        return cur_queryset

    def _pluck(self, serializer, attr=None):
        if attr is None:
            return serializer.child if is_many_serializer(serializer) else serializer
        return (
            getattr(serializer.child, attr)
            if is_many_serializer(serializer)
            else getattr(serializer, attr)
        )


class EagerFieldsAPIView(EagerFieldsViewMixin, GenericAPIView):
    pass
