from rest_framework import serializers


def is_many_serializer(serializer):
    return isinstance(serializer, serializers.ListSerializer)


def is_one_serializer(serializer):
    return isinstance(serializer, serializers.Serializer)


def is_serializer(serializer):
    return is_one_serializer(serializer) or is_many_serializer(serializer)


def is_model_serializer(serializer):
    return isinstance(serializer, serializers.ModelSerializer)


class EagerFieldsSerializerMixin(object):
    def __init__(self, *args, **kwargs):
        """
        The 'body_fields' context overrides all the query params
        """

        super().__init__(*args, **kwargs)

        body_fields_context = self.context.get("body_fields", None)
        if not body_fields_context:
            extra_fields_context = self.context.get("extra", None)
            if extra_fields_context:
                extra_fields_dict = self.context_to_dict(extra_fields_context)
                self.__class__.set_extra_fields(self, extra_fields_dict)

            exclude_fields_context = self.context.get("exclude", None)
            if exclude_fields_context:
                exclude_fields_dict = self.context_to_dict(exclude_fields_context)
                self.__class__.set_exclude_fields(self, exclude_fields_dict)

            fields_context = self.context.get("fields", None)
            if fields_context:
                fields_dict = self.context_to_dict(fields_context)
                self.__class__.set_fields(self, fields_dict)
        else:
            self.__class__.set_extra_fields(self, body_fields_context)
            self.__class__.set_fields(self, body_fields_context)

    @classmethod
    def set_extra_fields(cls, serializer, extra_fields_dict):

        cur_ser = cls._get_cur_ser(serializer)
        if not cur_ser:
            return

        extra_fields = getattr(cur_ser.Meta, "extra", None)

        # maybe this serializer doesn't define the eager_field property
        if not extra_fields:
            return

        kk = extra_fields_dict.keys()
        for k in kk:

            eager_field = extra_fields.get(k, None)

            # eager field is not an eager fields of the current serializer
            if not eager_field:
                continue

            # empty dict is False then True means this is not a dict leaf
            # so go deeper if it's a serializer
            nested_dict = extra_fields_dict[k]
            nested_field = eager_field.get("field", None)

            if nested_dict and is_serializer(nested_field):
                cls.set_extra_fields(nested_field, nested_dict)

            # now append the eager field to the serializer fields
            cur_ser.fields[k] = eager_field["field"]

    @classmethod
    def set_exclude_fields(cls, serializer, exclude_fields_dict):

        cur_ser = cls._get_cur_ser(serializer)
        if not cur_ser:
            return

        kk = exclude_fields_dict.keys()
        for k in kk:
            nested_dict = exclude_fields_dict[k]
            nested_field = cur_ser.fields.get(k, None)
            if nested_dict and is_serializer(nested_field):
                cls.set_exclude_fields(nested_field, nested_dict)
            else:
                if k in cur_ser.fields:  # leaf, remove it
                    cur_ser.fields.pop(k)

    @classmethod
    def set_fields(cls, serializer, fields_dict):

        cur_ser = cls._get_cur_ser(serializer)
        if not cur_ser:
            return

        kk = fields_dict.keys()
        for k in kk:
            nested_dict = fields_dict[k]
            nested_field = cur_ser.fields.get(k, None)
            if nested_dict and is_serializer(nested_field):
                cls.set_fields(nested_field, nested_dict)

        to_keep = set(kk)
        existing = set(cur_ser.fields.keys())

        for x in existing - to_keep:
            cur_ser.fields.pop(x)

    @classmethod
    def _get_cur_ser(cls, serializer):
        if not is_serializer(serializer):
            return None  # this should never occur
        return serializer.child if is_many_serializer(serializer) else serializer

    def context_to_dict(self, context) -> dict:
        """
        Get string params from context
        and merge them in a nested dict
        """
        l = self._string_to_list(context)
        d = dict()
        for kk in l:
            self._list_to_dict(kk, d)
        return d

    def _string_to_list(self, context) -> list:
        return [f.strip() for f in context.split(",")]

    def _list_to_dict(self, keys, store_dict=dict()) -> dict:
        """
        take a list of elements and merge them in a nested dict.
        Append the result if key already exists.
        The leaf of the nested dict must be empty one

        e.g.:
        input (call function for each elements of the main list)
        [[a.b.e],[a.b.g],[a.c.d]]

        output
        {
            'a':{
                'b': {
                    'e': {},
                    'g': {},
                },
                'c': {
                    'd':{}
                }
            }
        }
        """
        item, remaing_list = self._get_key_and_list(keys)
        if not len(remaing_list):
            if not item in store_dict:
                store_dict[item] = dict()
        else:
            if not item in store_dict:
                store_dict[item] = dict()
            else:
                store_dict[item] = dict(dict(), **store_dict[item])
            self._list_to_dict(remaing_list, store_dict[item])

    def _get_key_and_list(self, keys):
        """
        take the list of keys and
        return the first one and the list without it
        """

        # convert str to list, just the first run
        if isinstance(keys, str):
            keys = keys.split(".")

        # empty list, return
        if not len(keys):
            return None, []

        key = keys.pop(0)
        return key, keys


class EagerFieldsSerializer(EagerFieldsSerializerMixin, serializers.Serializer):
    pass
