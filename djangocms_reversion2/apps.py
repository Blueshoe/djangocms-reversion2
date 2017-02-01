# -*- coding: utf-8 -*-
from django.apps import apps as django_apps, AppConfig
from django.db.models.signals import post_save

import reversion
import inspect
from reversion import revisions as rev

from .signals import handle_cms_plugin_save, handle_title_save, handle_page_save


def _get_ancestor_class_names(klass, exclude=None):
    exclude = exclude or []
    return [k.__name__ for k in inspect.getmro(klass) if k.__name__ not in exclude]


class CMSReversion2Config(AppConfig):
    name = 'djangocms_reversion2'
    verbose_name = 'Django-CMS Reversion2'

    # we cannot make hard imports of the django-cms models
    CMS_MODELS_REGISTRATION = {
        'Page': {'registration': {},
                 'handler': (handle_page_save, 'save_page_reversion',)},
        'Title': {'registration': {},
                  'handler': (handle_title_save, 'save_title_reversion',)},
        'CMSPlugin': {'registration': {'follow': ('cmsplugin_ptr',)},
                      'handler': (handle_cms_plugin_save, 'save_{cmsplugin}_reversion',)},
    }

    def ready(self):
        self._setup()

    def _setup(self):
        cms_config = django_apps.get_app_config('cms')
        # make sure all required models are registered to reversion
        for model_name, options in self.CMS_MODELS_REGISTRATION.items():
            model_klass = cms_config.get_model(model_name)
            if model_name == 'CMSPlugin':
                self._connect_plugin_classes(model_klass, **options)
            else:
                post_save.connect(options['handler'][0], sender=model_klass, dispatch_uid=options['handler'][1])
                self._register_reversion_safe(model_klass, options['registration'])

    def _connect_plugin_classes(self, base_klass, handler, registration):
        def connect_subclasses(klass):
            for subclass in klass.__subclasses__():
                connect_subclasses(subclass)
            post_save.connect(handler[0], sender=klass, dispatch_uid=handler[1].format(cmsplugin=klass.__name__))
            self._register_reversion_safe(klass, registration)
        connect_subclasses(base_klass)

    def _register_reversion_safe(self, klass, registration):
        if not reversion.is_registered(klass):
            if klass.__name__ == 'CMSPlugin':
                reversion.register(klass)
            else:
                reversion.register(klass, **registration)
        else:
            if 'CMSPlugin' in _get_ancestor_class_names(klass, exclude='CMSPlugin'):
                opt_dict = rev._registered_models[rev._get_registration_key(klass)]._asdict()
                if not 'cmsplugin_ptr' in opt_dict['follow']:
                    opt_dict['follow'] += ('cmsplugin_ptr', )
                    rev._registered_models[rev._get_registration_key(klass)] = rev._VersionOptions(opt_dict)
                # reversion.unregister(klass)
                # reversion.register(klass, **registration)


