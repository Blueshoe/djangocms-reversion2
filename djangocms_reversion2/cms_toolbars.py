# -*- coding: utf-8 -*-
from cms.toolbar.items import LinkItem
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from cms.toolbar_pool import toolbar_pool
from cms.toolbar_base import CMSToolbar


@toolbar_pool.register
class Reversion2sModifier(CMSToolbar):

    def populate(self):
        page = self.request.current_page
        if page and page.publisher_is_draft:
            reversion_menu = self.toolbar.get_or_create_menu('djangocms_reversion2', _('Reversion'))
            reversion_menu.add_modal_item(
                _('Create a snapshot of current page'),
                url=self.get_language_url('admin:djangocms_reversion2_pagerevision_add'))

            reversion_menu.add_modal_item(
                _('Show history'),
                url=self.get_language_url('admin:djangocms_reversion2_pagerevision_changelist'))

            reversion_menu.add_break()
            reversion_menu.add_item(LinkItem(
                _('Create a snapshot of all unrevised pages'),
                url=reverse('admin:djangocms_reversion2_pagerevision_batch_add', kwargs={'pk': page.id})))

            reversion_menu.add_break()
            reversion_menu.add_modal_item(
                _('Download audit trail'),
                url=self.get_language_url('admin:djangocms_reversion2_download_audit'))

    def post_template_populate(self):
        pass

    def request_hook(self):
        pass

    def get_language_url(self, viewname):
        return '{url}?page_id={page_id}&language={lang}'.format(
            url=reverse(viewname=viewname),
            page_id=self.request.current_page.id,
            lang=self.current_lang or ''
        )
