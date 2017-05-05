# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import cms
from cms import api
from cms.models.titlemodels import Title
from cms.utils.conf import get_cms_setting
from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.encoding import force_text as u
from django.utils.translation import ugettext_lazy as _

from cms.models.pagemodel import Page
from treebeard.mp_tree import MP_Node


VERSION_ROOT_TITLE = '.~VERSION_ROOT_TITLE'


@python_2_unicode_compatible
class PageVersion(MP_Node):
    hidden_page = models.OneToOneField('cms.Page', on_delete=models.CASCADE, verbose_name=_('Hidden Page'),
                                       related_name='page_version', help_text=_('This Page object holds the versioned '
                                                                                'contents of this PageVersion.'))
    draft = models.ForeignKey('cms.Page', on_delete=models.CASCADE, verbose_name=_('Draft'),
                              related_name='page_versions', help_text=_('Current active draft.'))

    comment = models.TextField(_('Comment'), blank=True, help_text=_('Particular information concerning this Version'))
    title = models.CharField(_('Name'), blank=True, max_length=63)
    active = models.BooleanField(_('Active'), default=False,
                                 help_text=_('This the active version of current draft. There can be only one such '
                                             'version per Page version tree.'))

    def get_title(self):
        return self.title or 'implement'  # TODO

    @classmethod
    def create_version(cls, draft, version_parent=None, comment='', title=''):
        page_parent = cls.get_version_page_root()
        hidden_page = Page(parent=page_parent)
        draft._copy_attributes(hidden_page)
        hidden_page.save()

        for language in draft.get_languages():
            draft._copy_titles(hidden_page, language, False)
            draft._copy_contents(hidden_page, language)

        if version_parent:
            page_version = version_parent.add_child(draft=draft, comment=comment, title=title, active=version_parent.active)
            version_parent.deactivate()
        elif not draft.page_versions.exists():
            page_version = PageVersion.add_root(draft=draft, comment=comment, title=title, active=True)
        return page_version

    @classmethod
    def get_version_page_root(cls):
        try:
            return Page.objects.get(title_set__title=VERSION_ROOT_TITLE)
        except Page.DoesNotExist:
            return cms.api.create_page(VERSION_ROOT_TITLE, cms.constants.TEMPLATE_INHERITANCE_MAGIC, settings.LANGUAGES[0][0])

    def save(self, **kwargs):
        self.title = self.title or self.generate_title()
        self.comment = self.comment or self.generate_comment()
        super(PageVersion, self).save(**kwargs)

    def generate_title(self):
        return ''

    def generate_comment(self):
        return ''

    def deactivate(self, commit=True):
        self.active = False
        if commit:
            self.save()
    deactivate.alters_data = True

    def __str__(self):
        return self.title
