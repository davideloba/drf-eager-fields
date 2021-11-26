try:
    # Django 3.1 and above
    # https://stackoverflow.com/questions/43445171/importerror-cannot-import-name-classproperty?answertab=active#tab-top
    from django.utils.functional import classproperty
except ImportError:
    from django.utils.decorators import classproperty


def classproperty(classproperty):
    pass