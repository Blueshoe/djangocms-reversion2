# -*- coding: utf-8 -*-
from functools import update_wrapper

import cms
import datetime

from cms import api, constants
from cms.admin.pageadmin import PageAdmin
from cms.models import Page, Title, EmptyTitle
from cms.utils import get_cms_setting, get_language_from_request, get_language_list
from cms.utils import page_permissions
from collections import defaultdict
from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import MultipleObjectsReturned
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect, render_to_response, get_object_or_404, render
from django.template.loader import get_template
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _, ugettext
from sekizai.context import SekizaiContext

from djangocms_reversion2.forms import PageVersionForm
from djangocms_reversion2.models import PageVersion

BIN_NAMING_PREFIX = '.'
BIN_PAGE_NAME = BIN_NAMING_PREFIX + 'Papierkorb'
BIN_PAGE_LANGUAGE = 'de'
BIN_BUCKET_NAMING = BIN_NAMING_PREFIX + 'Eimer-%d.%m.%Y'


def revert_escape(txt, transform=True):
    """
    transform replaces the '<ins ' or '<del ' with '<div '
    :type transform: bool
    """
    html = txt.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&para;<br>", "\n")
    if transform:
        html = html.replace('<ins ', '<div ').replace('<del ', '<div ').replace('</ins>', '</div>')\
            .replace('</del>', '</div>')
    return html


class PageVersionAdmin(admin.ModelAdmin):
    form = PageVersionForm
    list_display = (
        '__str__', 'date', 'user', 'comment', 'revert_link',
        # 'diff_link'
    )
    list_display_links = None
    diff_template = 'admin/diff_old.html'
    diff_view_template = 'admin/diff.html'
    view_revision_template = 'admin/view_revision.html'

    # def get_urls(self):
    #     from django.conf.urls import url
    #
    #     def wrap(view):
    #         def wrapper(*args, **kwargs):
    #             return self.admin_site.admin_view(view)(*args, **kwargs)
    #         return update_wrapper(wrapper, view)
    #
    #     info = self.model._meta.app_label, self.model._meta.model_name
    #
    #     urlpatterns = [
    #         url(r'^$', wrap(self.changelist_view), name='%s_%s_changelist' % info),
    #         url(r'^add/(?P<page_id>\d+)?$', wrap(self.add_view), name='%s_%s_add' % info),
    #         url(r'^(.+)/history/$', wrap(self.history_view), name='%s_%s_history' % info),
    #         url(r'^(.+)/delete/$', wrap(self.delete_view), name='%s_%s_delete' % info),
    #         url(r'^(.+)/$', wrap(self.change_view), name='%s_%s_change' % info),
    #     ]
    #     return urlpatterns

    # def get_urls(self):
    #     urls = super(PageVersionAdmin, self).get_urls()
    #     admin_urls = [
    #         url(r'^add/(?P<page_id>\d+)/$', wrap(self.add_view), name='%s_%s_add' % info),
    #         # url(r'^audittrail/xlsx$', self.download_audit_trail_xlsx, name='djangocms_reversion2_download_audit_xlsx'),
    #         # url(r'^audittrail/$', self.download_audit_trail, name='djangocms_reversion2_download_audit'),
    #         # url(r'^revert/(?P<pk>\d+)$', self.revert, name='djangocms_reversion2_revert_page'),
    #         # url(r'^diff-view/page/(?P<page_pk>\d+)/base/(?P<base_pk>\d+)/comparison/(?P<comparison_pk>\d+)$',
    #         #     self.diff_view, name='djangocms_reversion2_diff_view'),
    #         # url(r'^view-revision/(?P<revision_pk>\d+)$', self.view_revision, name='djangocms_reversion2_view_revision'),
    #         # url(r'^diff/(?P<pk>\d+)$', self.diff, name='djangocms_reversion2_diff'),
    #         # url(r'^batch-add/(?P<pk>\w+)$', self.batch_add, name='djangocms_reversion2_pagerevision_batch_add'),
    #     ]
    #     return admin_urls + urls

    def get_urls(self):
        urls = super(PageVersionAdmin, self).get_urls()
        admin_urls = [
            url(r'^diff-view/page/(?P<page_pk>\d+)/left/(?P<left_pk>\d+)/right/(?P<right_pk>\d+)$',
                self.diff_view, name='djangocms_reversion2_diff_view'),
            url(r'^revert/(?P<pk>\d+)$', self.revert, name='djangocms_reversion2_revert_page')
        ]
        return admin_urls + urls

    def get_language_url(self, viewname, arguments={}):
        return '{url}?page_id={page_id}&language={lang}'.format(
            url=reverse(viewname=viewname, kwargs=arguments),
            page_id=self.request.current_page.id,
            lang=self.current_lang or ''
        )




    def revert(self, request, ** kwargs):
        #     # revert page to revision
        #     pk = kwargs.pop('pk')
        #     language = request.GET.get('language')
        #     page_revision = PageRevision.objects.get(id=pk)
        #
        #     if not revert_page(page_revision, request):
        #         messages.info(request, u'Page is already in this revision!')
        #         prev = request.META.get('HTTP_REFERER')
        #         if prev:
        #             return redirect(prev)
        return self.changelist_view(request, **kwargs)
        #
        #     # create a new revision if reverted to keep history correct
        #     # therefore mark a placeholder as dirty
        #     # TODO: in case of no placeholder?
        #     # page_revision.page.placeholders.first().mark_as_dirty(language)
        #     # creator = PageRevisionCreator(page_revision.page.pk, language, request, request.user,
        #     # ugettext(u'Restored') + ' ' + '#' + str(page_revision.pk))
        #     # creator.create_page_revision()
        #
        #
        # messages.info(request, _(u'You have succesfully reverted to {rev}').format(rev=page_revision))
        # return self.render_close_frame()
    # def batch_add(self, request, **kwargs):
    #     pk = kwargs.get('pk')
    #     language = kwargs.get('language')
    #     languages = [language] if language else None
    #     creator = PageRevisionBatchCreator(request, languages=languages, user=request.user)
    #     page_revisions = creator.create_page_revisions()
    #     num = len(page_revisions)
    #     messages.info(request, _(u'{num} unversioned pages have been versioned.').format(num=num))
    #     page = Page.objects.get(pk=pk)
    #     return redirect(page.get_absolute_url(language), permanent=True)

    def diff_view(self, request, **kwargs):
        # view which shows a revision on the left and one on the right
        # if the right revision has value zero: the current page is used!
        # -> page id is only neccessary in the utter case
        # if the comparison_pk is zero: the latest version is used
        # comparison_pk and base_pk are primary keys for *pages*!

        # also called left_pk
        left_pk = kwargs.pop('left_pk')
        # also called right_pk
        right_pk = kwargs.pop('right_pk')
        page_pk = kwargs.pop('page_pk')

        # get the draft we are talking about
        page_draft = get_object_or_404(Page, pk=page_pk).get_draft_object()

        # the right panel has id=0
        # -> use the draft of the page
        # -> else: fetch the page
        if int(right_pk) == 0:
            right_page = page_draft
        else:
            right_page = Page.objects.get(pk=right_pk)

        # the left panel has id=0
        # -> use the latest PageVersion draft of the page
        # -> else: fetch the page
        if int(left_pk) == 0:
            page_draft_versions = PageVersion.objects.filter(draft=page_draft).order_by('-hidden_page__changed_date')[:1]

            if page_draft_versions.count() > 0:
                left_page = page_draft_versions.first()
            else:
                messages.info(request, _(u'There are no snapshots for this page'))
                return self.render_close_frame()
        else:
            left_page = Page.objects.get(pk=left_pk)

        # list of page's revisions to show as the left sidebar
        revision_list = PageVersion.objects.filter(draft=page_draft)
        # group the revisions by date
        grouped_revisions = {}  # defaultdict(default_factory=list)
        for rev in revision_list.iterator():
            key = rev.hidden_page.changed_date.strftime("%Y-%m-%d")
            if key not in grouped_revisions.keys():
                grouped_revisions[key] = []
            grouped_revisions[key].append(rev)
        sorted_grouped_revisions = sorted(grouped_revisions.iteritems(), key=lambda (k, v): k, reverse=True)

        # differences between the placeholders

        # if not slot_html:
        #     messages.info(request, _(u'No diff between revision and current page detected'))
        #     return self.changelist_view(request, **kwargs)

        context = SekizaiContext({
            'left_page': left_page,
            'right_page': right_page,
            'is_popup': True,
            'page': page_draft.pk,
            'active_left_page_version_pk': left_page.pk,
            'request': request,
            'sorted_grouped_revisions': sorted_grouped_revisions,
            'active_language': kwargs.get('language', 'no language found'),
            'all_languages': page_draft.languages.split(',')
        })
        return render(request, self.diff_view_template, context=context)


    def add_view(self, request, form_url='', extra_context=None):
        # self.page = get_object_or_404(Page, pk=page_id)
        # print self.page.id
        # page = get_page(request, remove_params=False)
        # language = get_language_from_request(request)
        # if PageMarker.objects.filter(page=page, language=language).exists():
        #     messages.info(request, _('This page is already revised.'))
        #     return self.render_close_frame()
        # raise Http404
        return super(PageVersionAdmin, self).add_view(request, form_url=form_url, extra_context=extra_context)

    def get_changeform_initial_data(self, request):
        initial = super(PageVersionAdmin, self).get_changeform_initial_data(request)
        return initial

    def response_add(self, request, obj, post_url_continue=None):
        resp = super(PageVersionAdmin, self).response_add(request, obj, post_url_continue=post_url_continue)
        if IS_POPUP_VAR in request.POST:
            return self.render_close_frame()
        return resp

    def render_close_frame(self):
        return render_to_response('admin/close_frame.html', {})

    # def get_form(self, request, obj=None, **kwargs):
    #     form = super(PageVersionAdmin, self).get_form(request, obj=obj, **kwargs)
    #     form.fields['draft'].initial = self.page
    #     return form

    def get_queryset(self, request):
        qs = super(PageVersionAdmin, self).get_queryset(request)
        # # TODO review the following code
        # try:
        #     request.rev_page = getattr(request, 'rev_page', None) or Page.objects.get(pk=get_page(request))
        # except Page.DoesNotExist:
        #     request.rev_page = request.current_page
        # page = request.rev_page
        # language = get_language_from_request(request, current_page=page)
        # # page_id, language = page_lang(request)
        #
        # request.GET._mutable = True
        # request.GET.pop('cms_path', None)
        # request.GET._mutable = False
        #
        # if page:
        #     qs = qs.filter(page=page)
        # if language:
        #     qs = qs.filter(language=language)
        # qs = qs.select_related('page', 'revision')
        return qs

    def revert_link(self, obj):
        return '<a href="{url}" class="btn btn-primary">{label}</a>'.format(
            url=reverse('admin:djangocms_reversion2_revert_page', kwargs={'pk': obj.id}),
            label=_('Revert')
        )
    revert_link.short_description = _('Revert')
    revert_link.allow_tags = True

    # def diff_link(self, obj):
    #     return '<a href="{url}" class="btn btn-primary">{label}</a>'.format(
    #         url=reverse('admin:djangocms_reversion2_diff', kwargs={'pk': obj.id}),
    #         label=_('View diff')
    #     )
    # diff_link.short_description = _('Diff')
    # diff_link.allow_tags = True

    def comment(self, obj):
        return obj.comment
    comment.short_description = _('Comment')

    def user(self, obj):
        return obj.username
    user.short_description = _('By')

    def date(self, obj):
        return obj.hidden_page.changed_date.strftime('%d.%m.%Y %H:%M')
    date.short_description = _('Date')

admin.site.register(PageVersion, PageVersionAdmin)


class PageAdmin2(admin.site._registry.pop(Page).__class__):


    def change_template(self, request, object_id):
        page = get_object_or_404(self.model, pk=object_id)
        old_template = page.template
        response = super(PageAdmin2, self).change_template(request, object_id)
        page.refresh_from_db()
        if page.template != old_template:
            self._unmark_page(page)
        return response

    def publish_page(self, request, page_id, language):
        resp = super(PageAdmin2, self).publish_page(request, page_id, language)
        if not PageVersion.objects.filter(draft_id=page_id, clean=True).exists():
            PageVersion.create_version(Page.objects.get(id=page_id))
        return resp

    def delete_model(self, request, obj):
        # Retrieve the bin page or create it
        try:
            p = Page.objects.get(title_set__title=BIN_PAGE_NAME)
        except ObjectDoesNotExist:
            p = api.create_page(BIN_PAGE_NAME, constants.TEMPLATE_INHERITANCE_MAGIC, BIN_PAGE_LANGUAGE)
        except MultipleObjectsReturned:
            p = Page.objects.filter(title_set__title=BIN_PAGE_NAME).first()

        # is the page already under the ~BIN folder?
        is_in_bin = False
        q = obj
        while q:
            if q.title_set.filter(title=BIN_PAGE_NAME).count() > 0:
                is_in_bin = True
                break
            q = q.parent
        # if yes -> delete it
        if is_in_bin:
            obj.delete()
            p.fix_tree()
            return
        # else -> move it to the bin folder
        # split the contents of the bin into buckets (too many children will slow the javascript down
        bucket_title = datetime.datetime.now().strftime(BIN_BUCKET_NAMING)
        try:
            bucket = Page.objects.get(title_set__title=bucket_title)
        except ObjectDoesNotExist:
            bucket = api.create_page(bucket_title, constants.TEMPLATE_INHERITANCE_MAGIC,
                                               BIN_PAGE_LANGUAGE, parent=p)
        obj.move_page(bucket)
        p.fix_tree()
        obj.fix_tree()
        bucket.fix_tree()

    def get_tree(self, request):
        """
        Get html for the descendants (only) of given page or if no page_id is
        provided, all the root nodes.

        Used for lazy loading pages in cms.pagetree.js

        Permission checks is done in admin_utils.get_admin_menu_item_context
        which is called by admin_utils.render_admin_menu_item.
        """
        page_id = request.GET.get('pageId', None)
        site_id = request.GET.get('site', None)

        try:
            site_id = int(site_id)
            site = Site.objects.get(id=site_id)
        except (TypeError, ValueError, MultipleObjectsReturned,
                ObjectDoesNotExist):
            site = get_current_site(request)

        if page_id:
            page = get_object_or_404(self.model, pk=int(page_id))
            pages = page.get_children()
        else:
            pages = Page.get_root_nodes().filter(site=site, publisher_is_draft=True)#\
                #.exclude(title_set__title__startswith='X')

        pages = (
            pages
            .select_related('parent', 'publisher_public', 'site')
            .prefetch_related('children')
        )
        response = render_admin_rows(request, pages, site=site, filtered=False)
        return HttpResponse(response)

    def actions_menu(self, request, object_id):
        page = get_object_or_404(self.model, pk=object_id)
        paste_enabled = request.GET.get('has_copy') or request.GET.get('has_cut')
        can_change_advanced_settings = self.has_change_advanced_settings_permission(request, obj=page)
        has_change_permissions_permission = self.has_change_permissions_permission(request, obj=page)

        is_bin = page.title_set.filter(title__startswith=BIN_NAMING_PREFIX).count() > 0

        if is_bin:
            context = {
                'page': page,
                'page_is_restricted': True,
                'paste_enabled': False,
                'has_add_permission': False,
                'has_change_permission': False,
                'has_change_advanced_settings_permission':False,
                'has_change_permissions_permission': False,
                'has_move_page_permission': False,
                'has_delete_permission': self.has_delete_permission(request, obj=page),
                'CMS_PERMISSION': False,
            }
        else:
            context = {
                'page': page,
                'page_is_restricted': page.has_view_restrictions(),
                'paste_enabled': paste_enabled,
                'has_add_permission': page_permissions.user_can_add_subpage(request.user, target=page),
                'has_change_permission': self.has_change_permission(request, obj=page),
                'has_change_advanced_settings_permission': can_change_advanced_settings,
                'has_change_permissions_permission': has_change_permissions_permission,
                'has_move_page_permission': self.has_move_page_permission(request, obj=page),
                'has_delete_permission': self.has_delete_permission(request, obj=page),
                'CMS_PERMISSION': get_cms_setting('PERMISSION'),
            }

        return render(request, "admin/cms/page/tree/actions_dropdown.html", context)


def render_admin_rows(request, pages, site, filtered=False, language=None):
    """
    Used for rendering the page tree, inserts into context everything what
    we need for single item
    """
    user = request.user
    site = Site.objects.get_current()
    lang = get_language_from_request(request)
    permissions_on = get_cms_setting('PERMISSION')

    user_can_add = page_permissions.user_can_add_subpage
    user_can_move = page_permissions.user_can_move_page
    user_can_change = page_permissions.user_can_change_page
    user_can_change_advanced_settings = page_permissions.user_can_change_page_advanced_settings
    user_can_publish = page_permissions.user_can_publish_page

    template = get_template('admin/cms/page/tree/menu.html')
    bin_template = get_template('admin/bin_menu.html')

    if not language:
        language = get_language_from_request(request)

    filtered = filtered or request.GET.get('q')

    if filtered:
        # When the tree is filtered, it's displayed as a flat structure
        # therefore there's no concept of open nodes.
        open_nodes = []
    else:
        open_nodes = list(map(int, request.GET.getlist('openNodes[]')))

    languages = get_language_list(site.pk)

    page_ids = []

    for page in pages:
        page_ids.append(page.pk)

        if page.publisher_public_id:
            page_ids.append(page.publisher_public_id)

    cms_title_cache = defaultdict(dict)

    cms_page_titles = Title.objects.filter(
        page__in=page_ids,
        language__in=languages
    )

    for cms_title in cms_page_titles.iterator():
        # if cms_title.title.startswith(BIN_NAMING_PREFIX):
        #    for lang in languages:
        #        cms_title_cache[cms_title.page_id][lang] = cms_title
        # else:
        cms_title_cache[cms_title.page_id][cms_title.language] = cms_title

    def render_page_row(page):
        page_cache = cms_title_cache[page.pk]

        for language in languages:
            page_cache.setdefault(language, EmptyTitle(language=language))

        page.title_cache = cms_title_cache[page.pk]

        if page.publisher_public_id:
            publisher_cache = cms_title_cache[page.publisher_public_id]

            for language in languages:
                publisher_cache.setdefault(language, EmptyTitle(language=language))
            page.publisher_public.title_cache = publisher_cache

        if filtered:
            children = page.children.none()
        else:
            children = page.get_children()

        is_bin = page.title_set.filter(title__startswith=BIN_NAMING_PREFIX).exists()

        if is_bin:
            context = {
                'request': request,
                'page': page,
                'site': site,
                'lang': lang,
                'filtered': filtered,
                'metadata': '',
                'page_languages': None,
                'preview_language': None,
                'has_add_page_permission': False,
                'has_change_permission': False,
                'has_change_advanced_settings_permission': False,
                'has_publish_permission': False,
                'has_move_page_permission': False,
                'children': children,
                'site_languages': languages,
                'open_nodes': [],#open_nodes,
                'cms_current_site': site,
                'is_popup': (IS_POPUP_VAR in request.POST or IS_POPUP_VAR in request.GET)
            }
            return bin_template.render(context)

        has_move_page_permission = user_can_move(user, page)

        metadata = ""

        if permissions_on and not has_move_page_permission:
            # jstree metadata generator
            md = [('valid_children', False), ('draggable', False)]
            # just turn it into simple javascript object
            metadata = "{" + ", ".join(map(lambda e: "%s: %s" % (e[0],
            isinstance(e[1], bool) and str(e[1]) or e[1].lower() ), md)) + "}"



        context = {
            'request': request,
            'page': page,
            'site': site,
            'lang': lang,
            'filtered': filtered,
            'metadata': metadata,
            'page_languages': page.get_languages(),
            'preview_language': lang,
            'has_add_page_permission': user_can_add(user, target=page),
            'has_change_permission': user_can_change(user, page),
            'has_change_advanced_settings_permission': user_can_change_advanced_settings(user, page),
            'has_publish_permission': user_can_publish(user, page),
            'has_move_page_permission': has_move_page_permission,
            'children': children,
            'site_languages': languages,
            'open_nodes': open_nodes,
            'cms_current_site': site,
            'is_popup': (IS_POPUP_VAR in request.POST or IS_POPUP_VAR in request.GET)
        }
        return template.render(context)

    rendered = (render_page_row(page) for page in pages)
    return ''.join(rendered)

admin.site.register(Page, PageAdmin2)