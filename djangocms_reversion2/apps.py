# -*- coding: utf-8 -*-
import inspect

from django.apps import AppConfig
from .signals import connect_all_plugins



def _get_ancestor_class_names(klass, exclude=None):
    exclude = exclude or []
    return [k.__name__ for k in inspect.getmro(klass) if k.__name__ not in exclude]


class CMSReversion2Config(AppConfig):
    name = 'djangocms_reversion2'
    verbose_name = 'Django-CMS Reversion2'

    def ready(self):
        connect_all_plugins()

    def _setup(self):
        print('xxx')

