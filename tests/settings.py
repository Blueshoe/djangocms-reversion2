#!/usr/bin/env python
# -*- coding: utf-8 -*-

HELPER_SETTINGS = {
    'INSTALLED_APPS': [
        'djangocms_text_ckeditor',
        'djangocms_reversion2',
    ],
    'ALLOWED_HOSTS': ['localhost'],
    'CMS_LANGUAGES': {
        1: [{
            'code': 'en',
            'name': 'English',
        }]
    },
    'LANGUAGE_CODE': 'en',
}


def run():
    from djangocms_helper import runner
    runner.cms('djangocms_reversion2')

if __name__ == '__main__':
    run()
