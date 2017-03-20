# -*- coding: utf-8 -*-

import diff_match_patch as dmp
from cms.models.pagemodel import Page
from cms.models.placeholdermodel import Placeholder
from cms.plugin_rendering import ContentRenderer

from django.conf import settings
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_text as u

from djangocms_reversion2.models import PageRevision


def all_languages():
    return [l[0] for l in settings.LANGUAGES]


def get_page(request, remove_params=True):
    get = request.GET
    # our special get params need to be removed from QueryDict as ModelAdmin will break if they are still there
    if remove_params:
        get._mutable = True
        page_id = get.pop('page_id', [None])[0]
        # language = get.pop('language', [None])[0]
        get._mutable = False
    else:
        page_id = get.get('page_id', [None])[0]
        # language = get.get('language', [None])[0]
    # request.current_page = page_id
    return page_id  #, language


PAGE_MISMATCH, LANGUAGE_MISMATCH, MISSING_KWARG = 'page_mismatch', 'language_mismatch', 'missing_kwarg'


ERROR_MESSAGES = {
    PAGE_MISMATCH: _('You can only compare revisions of the same page.'),
    LANGUAGE_MISMATCH: _('You can only compare revisions of the same language.'),
    MISSING_KWARG: _('Please provide either page_revision2 or request.'),
}


class ComparatorException(Exception):
    def __init__(self, reason):
        super(ComparatorException, self).__init__(ERROR_MESSAGES.get(reason))


class PageRevisionComparator(object):
    def __init__(self, page_revision1, page_revision2=None, request=None):
        if page_revision2:
            if page_revision1.page != page_revision2.page:
                raise ComparatorException(PAGE_MISMATCH)
            if page_revision1.language != page_revision2.language:
                raise ComparatorException(LANGUAGE_MISMATCH)
        # request is necessary to render placeholders
        if not (page_revision2 or request):
            raise ComparatorException(MISSING_KWARG)

        self.page_revision1 = page_revision1
        self.page_revision2 = page_revision2
        self.page = page_revision1.page
        self.language = page_revision1.language
        self.request = request
        self.differ = dmp.diff_match_patch()

    @cached_property
    def placeholders(self):
        return Placeholder.objects.filter(page=self.page)

    @cached_property
    def slots(self):
        return self.placeholders.values_list('slot', flat=True)

    def get_rendered_placeholder(self, obj, slot):
        placeholder = self.placeholders.get(slot=slot)
        if isinstance(obj, PageRevision):
            return u(obj.placeholder_contents.get(placeholder=placeholder).html_content.body)
        if isinstance(obj, Page):
            context = SekizaiContext({'request': self.request})
            renderer = ContentRenderer(self.request)
            if hasattr(placeholder, '_plugins_cache'):
                del placeholder._plugins_cache
            body = renderer.render_placeholder(placeholder, context, language=self.language)
            return body.strip()

    @cached_property
    def rendered_placeholders(self):
        objs = (self.page_revision2 or self.page, self.page_revision1)
        return {slot: [self.get_rendered_placeholder(obj, slot) for obj in objs] for slot in self.slots}

    @cached_property
    def slot_diffs(self):
        return {slot: self.diff(*bodies) for slot, bodies in self.rendered_placeholders.items()}

    def diff(self, text1, text2):
        diffs = self.differ.diff_main(text1, text2)
        self.differ.diff_cleanupEfficiency(diffs)
        return diffs

    @cached_property
    def changed_slots(self):
        return [slot for slot, diffs in self.slot_diffs.items() if set(x for x, _ in diffs) != {0}]

    @cached_property
    def slot_html(self):
        return {slot: self.differ.diff_prettyHtml(diffs) for slot, diffs in self.slot_diffs.items()}