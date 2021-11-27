from rest_framework import serializers


def is_many_serializer(serializer):
    return isinstance(serializer, serializers.ListSerializer)

def is_one_serializer(serializer):
    return isinstance(serializer, serializers.Serializer)

def is_serializer(serializer):
    return is_one_serializer(serializer) or is_many_serializer(serializer)

def is_model_serializer(serializer):
    return isinstance(serializer, serializers.ModelSerializer)


class DynamicSerializer(serializers.Serializer):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        extra_fields_context = self.context.get('extra_fields', None)
        if extra_fields_context:
            extra_fields_dict = self.context_to_dict(extra_fields_context)
            self.__class__.set_extra_fields(self, extra_fields_dict)

        exclude_fields_context = self.context.get('exclude_fields', None)
        if exclude_fields_context:
            exclude_fields_dict = self.context_to_dict(exclude_fields_context)
            self.__class__.set_exclude_fields(self, exclude_fields_dict)

        only_fields_context = self.context.get('only_fields', None)
        if only_fields_context:
            only_fields_dict = self.context_to_dict(only_fields_context)
            self.__class__.set_only_fields(self, only_fields_dict)


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
    def set_only_fields(cls, serializer, only_fields_dict):

        cur_ser = cls._get_cur_ser(serializer)
        if not cur_ser:
            return

        kk = only_fields_dict.keys()
        for k in kk:
            nested_dict = only_fields_dict[k]
            nested_field = cur_ser.fields.get(k, None)
            if nested_dict and is_serializer(nested_field):  
                cls.set_only_fields(nested_field, nested_dict)

        to_keep = set(kk)
        existing = set(cur_ser.fields.keys())

        for x in existing - to_keep:
            cur_ser.fields.pop(x)


    @classmethod
    def _get_cur_ser(cls, serializer):
        if not is_serializer(serializer):
            return None # this should never occur
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
            keys = keys.split('.')

        # empty list, return
        if not len(keys):
            return None, []

        key = keys.pop(0)
        return key, keys
