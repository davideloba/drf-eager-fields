from django.db.models.query import Prefetch, QuerySet, prefetch_related_objects
from rest_framework.generics import GenericAPIView

from app.vendor.drf_dynamic_serializer.dynamic_serializer import is_many_serializer, is_model_serializer, is_serializer


class DynamicAPIView(GenericAPIView):


    def get_serializer_context(self):
        """"
        add our custom fields to the serializer context.
        if found in query args take that
        otherwise use the views parameters
        """
        context = super().get_serializer_context()

        for x in ['only_fields', 'exclude_fields', 'extra_fields']:
            params = self.request.query_params.get(x, '')
            if params:
                context[x] = params
            elif hasattr(self, 'serializer_' + x):
                context[x] = getattr(self, 'serializer_' + x)
        if self.request.data and self.request.data.get('fields', None):
            context['fields'] = self.request.data['fields']
        return context


    def get_queryset(self):
        queryset = super().get_queryset()
        serializer = self.get_serializer()
        return self._eager_load(serializer, queryset)


    def _eager_load(self, serializer, cur_queryset):

        fields = self._unplack(serializer, 'fields')
        
        for k in fields.keys():
            field = fields[k]
            if is_serializer(field):
                if is_model_serializer(self._unplack(field)):
                    source = field.source if field.source else k
                    relation = self._unplack(serializer, 'Meta').model._meta.get_field(source)

                    if relation.is_relation:
                        extra_field = self._unplack(serializer, 'extra_fields').get(k, None)
                        prefetch = extra_field.get('prefetch', None)  
                        if prefetch and isinstance(prefetch, Prefetch):
                            cur_queryset = cur_queryset.prefetch_related(
                                Prefetch(relation.name,
                                    queryset=self._eager_load(field, prefetch.queryset)
                                )
                            )
        return cur_queryset


    def _unplack(self, serializer, attr=None):
        if attr is None:
            return serializer.child if is_many_serializer(serializer) else serializer
        return getattr(serializer.child, attr) if is_many_serializer(serializer) else getattr(serializer, attr)
