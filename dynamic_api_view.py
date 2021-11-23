from rest_framework.generics import GenericAPIView


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
