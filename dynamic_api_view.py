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

        return context

    def get_queryset(self):
        """
        TODO:
        make fields prefetchable or
        selectable to improve
        database performance
        """
        queryset = super().get_queryset()
        serializer = self.get_serializer()
        d = {
            'prefetch_related' : '',
            'select_related' : ''
        }
        self._eager_load(serializer, d)
        prefetch = d['prefetch_related'][:-1] if d['prefetch_related'] else None
        select = d['select_related'][:-1] if d['select_related'] else None

        queryset = queryset.select_related(select).prefetch_related(prefetch)
        return queryset

    def _eager_load(self, serializer, d):
        fields = serializer.child.fields if is_many_serializer(serializer) else serializer.fields
        for k in fields.keys():
            field = fields[k]
            if is_serializer(field):
                many = True if is_many_serializer(field) else False
                if is_model_serializer(field if many else field.child):
                    rel = getattr(serializer.Meta.model, field.source if field.source else k)
                    if rel.field.many_to_many or rel.field.many_to_one:
                        d['prefetch_related'] += rel.field.name + '.'
                    elif rel.field.one_to_many or rel.field.one_to_one:
                        d['select_related'] += rel.field.name + '.'
                self._eager_load(field, d)
