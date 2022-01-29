from rest_framework import serializers


def is_many_serializer(serializer):
    return isinstance(serializer, serializers.ListSerializer)


def is_one_serializer(serializer):
    return isinstance(serializer, serializers.Serializer)


def is_serializer(serializer):
    return is_one_serializer(serializer) or is_many_serializer(serializer)


def is_model_serializer(serializer):
    ser = serializer.child if is_many_serializer(serializer) else serializer
    return (
        isinstance(ser, serializers.ModelSerializer)
        and hasattr(ser, "Meta")
        and hasattr(ser.Meta, "model")
    )


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

        current_serializer = cls._get_current_serializer(serializer)
        if not current_serializer:
            return

        kk = extra_fields_dict.keys()
        for k in kk:

            nested_dict = extra_fields_dict[k]

            extra_field = cls._get_extra_field(current_serializer, k)

            if not extra_field:
                return

            # empty dict is False then True means this is not a dict leaf
            # so go deeper if it's a serializer
            if nested_dict and is_serializer(extra_field):
                cls.set_extra_fields(extra_field, nested_dict)

            # now append the extra field to the serializer fields
            # if already in fields, this means it's a standard one,
            # no need to append it
            if k not in current_serializer.fields.keys():
                current_serializer.fields[k] = extra_field

    @classmethod
    def set_exclude_fields(cls, serializer, exclude_fields_dict):

        cur_ser = cls._get_current_serializer(serializer)
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

        cur_ser = cls._get_current_serializer(serializer)
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
    def _get_current_serializer(cls, serializer):
        if not is_serializer(serializer):
            return None  # this should never occur
        return serializer.child if is_many_serializer(serializer) else serializer

    @classmethod
    def _get_extra_field(cls, serializer, key):
        """
        Get the extra field from serializer.
        If not found in Meta.extra, try with the standard fields
        """
        extra_fields = (
            getattr(serializer.Meta, "extra", None)
            if hasattr(serializer, "Meta")
            else None
        )

        extra_field = extra_fields.get(key, None) if extra_fields else None
        if extra_field:
            return extra_field.get("field", None)

        extra_field = serializer.fields.get(key, None)
        return extra_field

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
