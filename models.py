# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from cms import constants
from django.db import models
from django.utils.encoding import python_2_unicode_compatible, force_text
from django.utils.translation import ugettext_lazy as _, get_language

from treebeard.mp_tree import MP_Node

from .utils import revise_page

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission

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
    dirty = models.BooleanField(_('Dirty'), default=False,
                                help_text=_('Only new PageVersions are not dirty of if a page has been reverted to a '
                                            'PageVersion.'))
    language = models.CharField(_('Language'), blank=True, max_length=20)
    owner = models.CharField(_("owner"), max_length=constants.PAGE_USERNAME_MAX_LENGTH, editable=False, default='script')

    def get_title(self):
        return self.title or 'implement'  # TODO

    @classmethod
    def create_version(cls, draft, language, version_parent=None, comment='', title=''):
        if draft.page_versions.filter(active=True, dirty=False, language=language).count() > 0:
            raise AssertionError('not dirty')

        # owner of the PageVersion is the last editor
        from cms.utils.permissions import get_current_user
        user = get_current_user()
        if user:
            try:
                owner = force_text(user)
            except AttributeError:
                # AnonymousUser may not have USERNAME_FIELD
                owner = "anonymous"
            else:
                # limit changed_by and created_by to avoid problems with Custom User Model
                if len(owner) > constants.PAGE_USERNAME_MAX_LENGTH:
                    changed_by = u'{0}... (id={1})'.format(owner[:constants.PAGE_USERNAME_MAX_LENGTH - 15], user.pk)
        else:
            owner = "script"

        # draft.page_versions.update(clean=False)
        hidden_page = revise_page(draft, language)
        if not version_parent and draft.page_versions.filter(language=language).exists():
            version_parent = draft.page_versions.get(active=True, language=language)

        if version_parent:
            page_version = version_parent.add_child(hidden_page=hidden_page, draft=draft, comment=comment, title=title,
                                                    active=version_parent.active, language=language, owner=owner)
            version_parent.deactivate()
        else:
            page_version = PageVersion.add_root(hidden_page=hidden_page, draft=draft, comment=comment, title=title,
                                                active=True, language=language, owner=owner)

        return page_version

    def save(self, **kwargs):
        self.title = self.title or self.generate_title()
        self.comment = self.comment or self.generate_comment()
        super(PageVersion, self).save(**kwargs)

    def generate_title(self):
        return ''

    def generate_comment(self):
        return ''

    @property
    def username(self):
        return self.hidden_page.changed_by

    def deactivate(self, commit=True):
        self.active = False
        if commit:
            self.save()
    deactivate.alters_data = True

    def __str__(self):
        if self.title:
            return self.title
        return self.hidden_page.get_title()

    class Meta:
        # example: user.has_perm('djangocms_reversion2.view_page_version')
        # permissions = (
        #     ('view_page_version', _('permission to view the page version')),
        #     ('delete_page_version', _('permission to delete the page version')),
        #     ('create_page_version', _('permission to create the page version')),
        #     ('edit_page_version', _('permission to edit a page version')),
        #     ('revert_to_page_version', _('permission to revert a page to the page version')),
        # )
        default_permissions = ('add', 'change', 'delete')


# content_type = ContentType.objects.get_for_model(PageVersion)
# permission = Permission.objects.create(
#     codename='can_create',
#     name='Can Publish Posts',
#     content_type=content_type,
# )
