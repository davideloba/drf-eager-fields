from rest_framework import serializers


def is_many_serializer(serializer):
    return isinstance(serializer, serializers.ListSerializer)

def is_one_serializer(serializer):
    return isinstance(serializer, serializers.Serializer)

def is_serializer(serializer):
    return is_one_serializer(serializer) or is_many_serializer(serializer)

def is_model_serializer(serializer):
    return isinstance(serializer, serializers.ModelSerializer)


def get_key_and_list(keys):
    """
    take the list of keys and 
    return the first one and the list without it
    """

    # convert str to list, just the first run
    if isinstance(keys, str):
        keys = keys.split('.')

    # empty list, return
    if not len(keys):
        return None, []

    key = keys.pop(0)
    return key, keys


def recursive_exclude(fields, exclude_keys):
    # TODO: use dict instead of list
    exclude_key, remaining_exclude_keys = get_key_and_list(exclude_keys)

    if exclude_key in fields:
        field = fields.get(exclude_key)
    else:
        return None

    if len(remaining_exclude_keys) and is_serializer(field):
        return recursive_exclude(field.child.fields if is_many_serializer(field) else field.fields, remaining_exclude_keys)
    else:
        fields.pop(exclude_key)

    return fields


class DynamicSerializer(serializers.Serializer):

    def __init__(self, *args, **kwargs):
        """
        As suggested by DRF, we modify fields
        in the constructor of the serializer

        see https://www.django-rest-framework.org/api-guide/serializers/#dynamically-modifying-fields
        """

        super().__init__(*args, **kwargs)

        extra_fields_context = self.context.get('extra_fields', None)
        if extra_fields_context:
            extra_fields_dict = self.context_to_dict(extra_fields_context)
            self.__class__.set_extra_fields(self, extra_fields_dict)

        exclude_fields_context = self.context.get('exclude_fields', None)
        if exclude_fields_context:
            exclude_fields_dict = self.context_to_dict(exclude_fields_context)
            self.__class__.set_exclude_fields(self, exclude_fields_dict)

        if self.context.get('only_fields'):
            only_keys_dict = self.context_to_dict(self.context.get('only_fields'))
            if only_keys_dict:
                self._set_only(self.fields, only_keys_dict)


    @classmethod
    def set_extra_fields(cls, serializer, extra_fields_dict):

        cur_ser = cls._get_cur_ser(serializer)
        if not cur_ser:
            return

        kk = extra_fields_dict.keys()
        for k in kk:

            # maybe this serializer doesn't define the extra_field property
            if not cur_ser.extra_fields:
                continue

            extra_field = cur_ser.extra_fields.get(k, None)
            
            # extra field is not an extra fields of the serializer
            if not extra_field:
                continue

            # empty dict is False then True means this is not a dict leaf
            # so go deeper if it's a serializer
            nested_dict = extra_fields_dict[k]
            nested_field = extra_field.get('field', None)
            if nested_dict and is_serializer(nested_field):  
                cls.set_extra_fields(nested_field, nested_dict)

            # now append the extra field
            cur_ser.fields[k] = extra_field['field']


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
                if k in cur_ser.fields: # leaf, remove it
                    cur_ser.fields.pop(k)


    @classmethod
    def _get_cur_ser(cls, serializer):
        if not is_serializer(serializer):
            return None # this should never occur
        return serializer.child if is_many_serializer(serializer) else serializer


    def _set_only(self, fields, only_keys_dict):
        """
        remove fields not in the only_keys dict
        """
        kk = only_keys_dict.keys()
        for k in kk:
            if only_keys_dict[k]: # empty dict is False
                if k in fields:
                    field = fields.get(k)
                else:
                    continue
                if is_serializer(field):
                    self._set_only(field.child.fields if is_many_serializer(field) else field.fields, only_keys_dict[k])

        to_keep = set(kk)
        existing = set(fields.keys())

        for x in existing - to_keep:
            fields.pop(x)

        return fields

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
        return [f.strip() for f in context.split(',')]

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
        item, remaing_list = get_key_and_list(keys)
        if not len(remaing_list):
            if not item in store_dict:
                store_dict[item] = dict()
        else:
            if not item in store_dict:
                store_dict[item] = dict()
            else:
                store_dict[item] = dict(dict(), **store_dict[item])
            self._list_to_dict(remaing_list, store_dict[item])