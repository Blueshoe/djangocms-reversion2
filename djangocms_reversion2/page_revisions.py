# -*- coding: utf-8 -*-
from itertools import groupby
from operator import itemgetter

from cms.models import CMSPlugin
from cms.models import Title
from cms.models.pagemodel import Page
from cms.models.placeholdermodel import Placeholder
from cms.plugin_rendering import ContentRenderer
from django.db import transaction
from django.template.context import Context
from django.utils.encoding import smart_text as u
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property

import reversion
from sekizai.context import SekizaiContext

from reversion.signals import post_revision_commit


MAX_ROOT_MARK = 'max root mark'
BATCH_CREATE_COMMENT = _('Created in batch')
AUTO_REVISION_COMMENT = _('Autocreated because of reversion of unsaved draft')


def update_max_root(plugins_qs=None):
    # This is done because plugins can be deleted, but must still be revertable with the same path as before.
    # The max_path marker root ensures that new root plugins must have a path that is lexicographically higher than
    # any path of any plugin in a revision.
    if plugins_qs is None:
        plugins_qs = CMSPlugin.get_root_nodes()
    if not plugins_qs.exists():
        return None
    try:
        max_root = CMSPlugin.get_root_nodes().get(plugin_type=MAX_ROOT_MARK)
    except CMSPlugin.DoesNotExist:
        max_root = None
    max_plugin = plugins_qs.filter(depth=1).latest('path')
    if not max_root or max_root.path < max_plugin.path:
        if max_root:
            max_root.delete()
        return CMSPlugin.objects.create(plugin_type=MAX_ROOT_MARK, language=MAX_ROOT_MARK)
    return None


class PageRevisionError(Exception):
    pass


class PageRevisionCreator(object):
    def __init__(self, page_id, language, request=None, user=None, comment=''):
        if not page_id:
            raise PageRevisionError(u'Invalid page_id: "{page_id}"'.format(page_id=u(page_id)))
        if not language:
            raise PageRevisionError(u'Invalid language: "{language}"'.format(language=u(language)))
        self.request = request
        self.page_id = page_id
        self.language = language
        self.user = user or (request.user if request else None)
        self.comment = comment
        self._revision = None
        self._page_revision = None

    @cached_property
    def page_revision(self):
        return self._page_revision or self.create_page_revision()

    def create_page_revision(self):
        self._page_revision = PageRevision.objects.create(
            page_id=self.page_id, language=self.language, revision=self.revision)
        create_placeholder_contents(self._page_revision, self.request)
        update_max_root(self.get_cms_plugins())
        mark_page_revised(self._page_revision)
        return self._page_revision

    @cached_property
    def revision(self):
        return self._revision or self._create_revision()

    def _create_revision(self):
        post_revision_commit.connect(self._handle_revision_commit, dispatch_uid='handle_revision_commit')
        with reversion.create_revision():
            reversion.set_comment(self.comment)
            reversion.set_user(self.user)
            # revision plugins and title for given language
            for plugin_instance in self.get_plugin_instances():
                reversion.add_to_revision(plugin_instance)
            reversion.add_to_revision(self.get_page_title())
        post_revision_commit.disconnect(dispatch_uid='handle_revision_commit')
        try:
            assert self._revision is not None
        except AssertionError:
            raise PageRevisionError(_(u'Revision creation failed'))
        return self._revision

    def _handle_revision_commit(self, sender, revision, versions, **kwargs):
        if not versions:
            revision.delete()
            raise PageRevisionError(u'There is no content for this revision')
        self._revision = revision

    def get_cms_plugins(self):
        return CMSPlugin.objects.filter(placeholder__page=self.page_id, language=self.language)

    def get_plugin_instances(self):
        return filter(None, [plugin.get_plugin_instance()[0] for plugin in self.get_cms_plugins()])

    def get_page_title(self):
        return Title.objects.get(page_id=self.page_id, language=self.language)


class PageRevisionBatchCreator(object):
    def __init__(self, request, languages=None, user=None, comment=BATCH_CREATE_COMMENT):
        self.languages = set(languages) if languages else set([])
        self.request = request
        self.user = user or request.user
        self.comment = comment

    def create_page_revisions(self):
        page_revisions = []
        for page_id, language in self.page_languages():
            creator = PageRevisionCreator(page_id, language, self.request, self.user, self.comment)
            page_revisions.append(creator.page_revision)
        return page_revisions

    def page_languages(self):
        page_markers = sorted(PageMarker.objects.values_list('page_id', 'language'))
        page, lang = itemgetter(0), itemgetter(1)
        revised_pages = dict((k, set(map(lang, g))) for k, g in groupby(page_markers, key=page))

        pages = Page.objects.filter(publisher_is_draft=True)
        for page in pages:
            revise_languages = set(page.get_languages()) - revised_pages.get(page.id, set([]))
            if self.languages:
                revise_languages &= self.languages
            for language in revise_languages:
                yield page.id, language


def create_placeholder_contents(page_revision, request):
    # persist rendered html content for each placeholder for later use in diff
    placeholders = Placeholder.objects.filter(page=page_revision.page_id)
    for ph in placeholders:
        body = placeholder_html(ph, request, page_revision.language)
        PageRevisionPlaceholderContent.objects.create(
            page_revision=page_revision,
            placeholder=ph,
            html_content=HtmlContent.objects.get_or_create(body=body)[0]
        )


def placeholder_html(placeholder, request, language):
    if hasattr(placeholder, '_plugins_cache'):
        del placeholder._plugins_cache
    context = SekizaiContext({'request': request})
    renderer = ContentRenderer(request)
    return renderer.render_placeholder(placeholder, context, language=language).strip()
