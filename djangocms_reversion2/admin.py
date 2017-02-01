# -*- coding: utf-8 -*-
from cms.admin.pageadmin import PageAdmin
from cms.models.pagemodel import Page
from cms.utils import get_language_from_request
from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.options import IS_POPUP_VAR
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render_to_response, get_object_or_404, render
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _

from djangocms_reversion2.forms import PageRevisionForm
from djangocms_reversion2.models import PageMarker
from djangocms_reversion2.page_revisions import PageRevisionBatchCreator, PageRevisionCreator, revert_page
from djangocms_reversion2.utils import get_page, PageRevisionComparator
from .models import PageRevision


class PageRevisionAdmin(admin.ModelAdmin):
    form = PageRevisionForm
    list_display = ('__str__', 'date', 'user', 'comment', 'revert_link', 'diff_link')
    list_display_links = None
    diff_template = 'admin/diff.html'

    def get_urls(self):
        urls = super(PageRevisionAdmin, self).get_urls()
        admin_urls = [
            url(r'^audittrail/$', self.download_audit_trail, name='djangocms_reversion2_download_audit'),
            url(r'^revert/(?P<pk>\d+)$', self.revert, name='djangocms_reversion2_revert_page'),
            url(r'^diff/(?P<pk>\d+)$', self.diff, name='djangocms_reversion2_diff'),
            url(r'^batch-add/(?P<pk>\w+)$', self.batch_add, name='djangocms_reversion2_pagerevision_batch_add'),
        ]
        return admin_urls + urls

    def download_audit_trail(self, request):
        self.set_page_lang(request)
        return TemplateResponse(request, 'admin/download_audit_trail.html', {})

    def revert(self, request, **kwargs):
        pk = kwargs.pop('pk')
        page_revision = PageRevision.objects.get(id=pk)

        if not revert_page(page_revision, request):
            messages.info(request, u'Page is already in this revision!')
            prev = request.META.get('HTTP_REFERER')
            if prev:
                return redirect(prev)
            return self.changelist_view(request, **kwargs)

        messages.info(request, _(u'You have succesfully reverted to {rev}').format(rev=page_revision))
        return self.render_close_frame()

    def diff(self, request, **kwargs):
        pk = kwargs.pop('pk')
        page_revision = PageRevision.objects.get(id=pk)

        prc = PageRevisionComparator(page_revision, request=request)
        slot_html = {slot: html for slot, html in prc.slot_html.items() if slot in prc.changed_slots}

        if not slot_html:
            messages.info(request, _(u'No diff between revision and current page detected'))
            return self.changelist_view(request, **kwargs)

        context = {
            'title': _(u'Diff current page and page revision #{pk}').format(pk=pk),
            'slot_html': slot_html
        }
        return render(request, self.diff_template, context=context)

    def batch_add(self, request, **kwargs):
        pk = kwargs.get('pk')
        language = kwargs.get('language')
        languages = [language] if language else None
        creator = PageRevisionBatchCreator(request, languages=languages, user=request.user)
        page_revisions = creator.create_page_revisions()
        num = len(page_revisions)
        messages.info(request, _(u'{num} unversioned pages have been versioned.').format(num=num))
        page = Page.objects.get(pk=pk)
        return redirect(page.get_absolute_url(language), permanent=True)

    def add_view(self, request, form_url='', extra_context=None):
        page = get_page(request, remove_params=False)
        language = get_language_from_request(request)
        if PageMarker.objects.filter(page=page, language=language).exists():
            messages.info(request, _('This page is already revised.'))
            return self.render_close_frame()
        return super(PageRevisionAdmin, self).add_view(request, form_url=form_url, extra_context=extra_context)

    def response_add(self, request, obj, post_url_continue=None):
        resp = super(PageRevisionAdmin, self).response_add(request, obj, post_url_continue=post_url_continue)
        if IS_POPUP_VAR in request.POST:
            return self.render_close_frame()
        return resp

    def render_close_frame(self):
        return render_to_response('admin/close_frame.html', {})

    def get_form(self, request, obj=None, **kwargs):
        form = super(PageRevisionAdmin, self).get_form(request, obj=obj, **kwargs)
        form.request = request
        return form

    def get_queryset(self, request):
        qs = super(PageRevisionAdmin, self).get_queryset(request)
        page = request.current_page
        language = get_language_from_request(request, current_page=page)
        # page_id, language = page_lang(request)
        if page:
            qs = qs.filter(page=page)
        if language:
            qs = qs.filter(language=language)
        qs = qs.select_related('page', 'revision')
        return qs

    def revert_link(self, obj):
        return '<a href="{url}" class="btn btn-primary">{label}</a>'.format(
            url=reverse('admin:djangocms_reversion2_revert_page', kwargs={'pk': obj.id}),
            label=_('Revert')
        )
    revert_link.short_description = _('Revert')
    revert_link.allow_tags = True

    def diff_link(self, obj):
        return '<a href="{url}" class="btn btn-primary">{label}</a>'.format(
            url=reverse('admin:djangocms_reversion2_diff', kwargs={'pk': obj.id}),
            label=_('View diff')
        )
    diff_link.short_description = _('Diff')
    diff_link.allow_tags = True

    def comment(self, obj):
        return obj.revision.comment
    comment.short_description = _('Comment')

    def user(self, obj):
        return obj.revision.user
    user.short_description = _('By')

    def date(self, obj):
        return obj.revision.date_created.strftime('%d.%m.%Y %H:%M')
    date.short_description = _('Date')

admin.site.register(PageRevision, PageRevisionAdmin)


class PageAdmin2(PageAdmin):
    def post_move_plugin(self, request, source_placeholder, target_placeholder, plugin):
        super(PageAdmin2, self).post_move_plugin(request, source_placeholder, target_placeholder, plugin)
        self._unmark_plugin(plugin)

    def post_delete_plugin(self, request, plugin):
        super(PageAdmin2, self).post_delete_plugin(request, plugin)
        self._unmark_plugin(plugin)

    # def post_add_plugin(self, request, plugin):
    #     super(PageAdmin2, self).post_add_plugin(request, plugin)
    #     self._unmark_plugin(plugin)

    # def post_edit_plugin(self, request, plugin):
    #     super(PageAdmin2, self).post_edit_plugin(request, plugin)
    #     self._unmark_plugin(plugin)

    def post_clear_placeholder(self, request, placeholder):
        super(PageAdmin2, self).post_clear_placeholder(request, placeholder)
        self._unmark_page(placeholder.page)

    def change_template(self, request, object_id):
        page = get_object_or_404(self.model, pk=object_id)
        old_template = page.template
        response = super(PageAdmin2, self).change_template(request, object_id)
        page.refresh_from_db()
        if page.template != old_template:
            self._unmark_page(page)
        return response

    def _unmark_page(self, page):
        PageMarker.unmark(page)

    def _unmark_plugin(self, plugin):
        PageMarker.unmark(plugin.placeholder.page, plugin.language)

    def publish_page(self, request, page_id, language):
        resp = super(PageAdmin2, self).publish_page(request, page_id, language)
        if not PageMarker.objects.filter(page_id=page_id, language=language).exists():
            prc = PageRevisionCreator(page_id, language, request, comment='Autocreated when published')
            prc.create_page_revision()
        return resp

admin.site.unregister(Page)
admin.site.register(Page, PageAdmin2)
