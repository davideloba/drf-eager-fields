from rest_framework import serializers


def is_many_serializer(serializer):
    return isinstance(serializer, serializers.ListSerializer)

def is_one_serializer(serializer):
    return isinstance(serializer, serializers.Serializer)

def is_serializer(serializer):
    return is_one_serializer(serializer) or is_many_serializer(serializer)


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


def recursive_extra(serializer, extra_keys):
    # TODO: use dict instead of list
    extra_key, remaining_extra_keys = get_key_and_list(extra_keys)

    is_many = is_many_serializer(serializer)
    
    if is_many:
        extra_field = serializer.child.extra_fields.get(extra_key, None)
    else:
        extra_field = serializer.extra_fields.get(extra_key, None)
    if extra_field is None:
        return None

    if len(remaining_extra_keys) and is_serializer(extra_field.get('field', None)):
        recursive_extra(extra_field['field'], remaining_extra_keys)
    
    if is_many:
        serializer.child.fields[extra_key] = extra_field['field']
    else:
        serializer.fields[extra_key] = extra_field['field']


class DynamicSerializer(serializers.Serializer):

    def __init__(self, *args, **kwargs):
        """
        As suggested by DRF, we modify fields
        in the constructor of the serializer

        see https://www.django-rest-framework.org/api-guide/serializers/#dynamically-modifying-fields
        """

        super().__init__(*args, **kwargs)

        if self.context.get('extra_fields'):
            extra_key_list = [f.strip() for f in self.context.get('extra_fields').split(',')]
            for extra_keys in extra_key_list:
                recursive_extra(self, extra_keys)

        if self.context.get('exclude_fields'):
            exclude_keys_list = [f.strip() for f in self.context.get('exclude_fields').split(',')]
            for exclude_keys in exclude_keys_list:
                recursive_exclude(self.fields, exclude_keys)

        if self.context.get('only_fields'):
            only_keys_list = self._strings_to_list('only_fields')
            only_keys_dict = dict()
            for only_keys in only_keys_list:
                self._list_to_dict(only_keys, only_keys_dict)
            if only_keys_dict:
                self._set_only(self.fields, only_keys_dict)

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
        
    def _strings_to_list(self, key):
        return [f.strip() for f in self.context.get(key).split(',')]

    def _list_to_dict(self, keys, store_dict=dict()):
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