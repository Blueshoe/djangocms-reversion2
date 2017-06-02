# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from itertools import chain

import time
from cms.constants import PUBLISHER_STATE_DIRTY
from cms.utils import page as page_utils
from cms.utils.page import get_available_slug
from django.conf import settings

from cms import api, constants
from cms.exceptions import PublicIsUnmodifiable
from cms.extensions import extension_pool
from cms.models import Page, Placeholder, Title, menu_pool, copy_plugins_to, Q, ACCESS_DESCENDANTS, \
    ACCESS_PAGE_AND_DESCENDANTS, ACCESS_CHILDREN, ACCESS_PAGE_AND_CHILDREN, ACCESS_PAGE, PagePermission
from cms.utils.conf import get_cms_setting
from django.db import IntegrityError
from django.db import transaction



VERSION_ROOT_TITLE = '.~VERSIONS'

VERSION_FIELD_DEFAULTS = {
    'Page': {
        'path': None,
        'depth': None,
        'numchild': 0,
        'publisher_public_id': None,
        'is_home': False,
        'reverse_id': None,
        'in_navigation': False,
    },
    'Title': {
        'published': False,
        'publisher_public': None,
        'has_url_overwrite': False,
        'slug': page_utils.get_available_slug,
    }
}


def _copy_model(instance, **attrs):
    instance.pk = None
    for field, value in chain(attrs.items(), VERSION_FIELD_DEFAULTS.get(instance.__class__.__name__, {}).items()):
        try:
            value = value(instance)
        except TypeError:
            pass
        setattr(instance, field, value)
    instance.save()
    return instance


def get_version_page_root(site):
    try:
        return Page.objects.get(title_set__title=VERSION_ROOT_TITLE, site=site)
    except Page.DoesNotExist:
        return api.create_page(
            VERSION_ROOT_TITLE, constants.TEMPLATE_INHERITANCE_MAGIC, settings.LANGUAGES[0][0], site=site)


def revise_page(page, language):
    """
    Copy a page [ and all its descendants to a new location ]
    Doesn't checks for add page permissions anymore, this is done in PageAdmin.

    Note for issue #1166: when copying pages there is no need to check for
    conflicting URLs as pages are copied unpublished.
    --> get_queryset_by_path(...).get() will fail
    """
    if not page.publisher_is_draft:
        raise PublicIsUnmodifiable("revise page is not allowed for public pages")

    # if the active version is not dirty -> do not create a revision
    if page.page_versions.filter(active=True, dirty=False, language=language).count() > 0:
        return None

    # avoid muting input param
    page = Page.objects.get(pk=page.pk)

    site = page.site
    version_page_root = get_version_page_root(site=site)

    origin_id = page.pk  # still needed to retrieve titles, placeholders

    # create a copy of this page by setting pk = None (=new instance)
    new_page = _copy_model(page, parent=version_page_root)

    # copy titles of this page
    for title in Title.objects.filter(page=origin_id, language=language).iterator():
        _copy_model(title, page=new_page)

    print(new_page.title_set.all())

    # copy the placeholders (and plugins on those placeholders!)
    for ph in Placeholder.objects.filter(page=origin_id).iterator():
        plugins = ph.get_plugins_list(language=language)
        try:
            # why might the placeholder already exist?
            ph = new_page.placeholders.get(slot=ph.slot)
        except Placeholder.DoesNotExist:
            ph = _copy_model(ph)
            page.placeholders.add(ph)
        if plugins:
            copy_plugins_to(plugins, ph, to_language=language)

    extension_pool.copy_extensions(Page.objects.get(pk=origin_id), new_page, languages=[language])

    new_page = new_page.move(version_page_root, pos="last-child")

    # Copy the permissions from the old page and its parents to the new page

    # MAP the parent permission to new child permissions
    mapping = {
        ACCESS_DESCENDANTS: ACCESS_PAGE_AND_DESCENDANTS,
        ACCESS_CHILDREN: ACCESS_PAGE
    }
    # for_page sadly doesn't work as expected
    if get_cms_setting('PERMISSION'):
        origin_page = Page.objects.get(pk=origin_id)
        # store the new permissions
        new_permissions = []
        # Copy page's permissions
        for perm in origin_page.pagepermission_set.all():
            new_permissions.append(_copy_model(perm, page=new_page))
        # the permission of all relevant parents
        perms = inherited_permissions(origin_page)
        for perm in perms:
            latest = _copy_model(perm, page=new_page)
            if latest.grant_on in mapping.keys():
                new_permissions.append(latest)
                # apply the mapping (see some lines above)
                latest.grant_on = mapping[latest.grant_on]
                latest.save()

    # invalidate the menu for this site
    menu_pool.clear(site_id=site.pk)
    return new_page


def inherited_permissions(page):
    """Returns queryset containing all instances somehow connected to given
    page.
    """
    paths = [
        page.path[0:pos]
        for pos in range(0, len(page.path), page.steplen)[1:]
    ]
    parents = Q(page__path__in=paths) & (Q(grant_on=ACCESS_DESCENDANTS) | Q(grant_on=ACCESS_PAGE_AND_DESCENDANTS))
    direct_parents = Q(page__pk=page.parent_id) & (Q(grant_on=ACCESS_CHILDREN) | Q(grant_on=ACCESS_PAGE_AND_CHILDREN))
    #page_qs = Q(page=page) & (Q(grant_on=ACCESS_PAGE_AND_DESCENDANTS) | Q(grant_on=ACCESS_PAGE_AND_CHILDREN) |
    #                          Q(grant_on=ACCESS_PAGE))
    query = (parents | direct_parents)
    return PagePermission.objects.filter(query).order_by('-page__depth')


def revert_page(page_version, language):
    from .models import PageVersion
    # copy all relevant attributes from hidden_page to draft
    source = page_version.hidden_page
    target = page_version.draft
    # source = Page()
    # target = Page()

    _copy_titles(source, target, language)
    source._copy_contents(target, language)

    source._copy_attributes(target)

    PageVersion.objects.filter(draft=page_version.draft, language=language).update(active=False)
    page_version.active = True
    page_version.dirty = False
    page_version.save()


def _copy_titles(source, target, language):
    """
    Copy all the titles to a new page (which must have a pk).
    The title has a published attribute that needs to be set to false.
        There is also the publisher_is_draft attribute
    :param target: The page where the new titles should be stored
    """

    assert source.publisher_is_draft
    assert target.publisher_is_draft

    old_titles = dict(target.title_set.filter(language=language).values_list('language', 'pk'))
    for title in source.title_set.filter(language=language):

        # If an old title exists, overwrite. Otherwise create new
        target_pk = old_titles.pop(title.language, None)
        title.pk = target_pk
        title.page = target

        # target fields that we keep
        target_title = Title.objects.get(pk=target_pk) if target_pk else None
        title.slug = getattr(target_title, 'slug', '')
        title.path = getattr(target_title, 'path', '')
        title.has_url_overwrite = getattr(target_title, 'has_url_overwrite', False)
        title.redirect = getattr(target_title, 'redirect', None)
        title.publisher_public_id = getattr(target_title, 'publisher_public_id', None)
        # has to be false
        title.published = getattr(target_title, 'published', False)

        # dirty since we are overriding current draft
        title.publisher_state = PUBLISHER_STATE_DIRTY

        title.save()

    if old_titles:
        Title.objects.filter(id__in=old_titles.values()).delete()


def is_version_page(page):
    version_page_root = get_version_page_root(page.site)
    return page.is_descendant_of(version_page_root)


def get_draft_of_version_page(page):
    return page.page_version.draft


def revise_all_pages():
    """
    Revise all pages (exclude the bin)
    :return: number of created revisions
    """
    from .admin import BIN_NAMING_PREFIX
    from .models import PageVersion
    num = 0
    integrity_errors = 0
    for page in Page.objects.all().exclude(title_set__title__startswith=BIN_NAMING_PREFIX).exclude(
                                     parent__title_set__title__startswith=BIN_NAMING_PREFIX).iterator():
        draft = page.get_draft_object()
        for language in page.languages.split(','):
            try:
                try:
                    # this is necessary, because an IntegrityError makes a rollback necessary
                    #with transaction.atomic():
                    PageVersion.create_version(draft, language, version_parent=None, comment='batch created', title='auto')
                except IntegrityError as e:
                    print(e)
                    integrity_errors += 1
                else:
                    print("num: {}, \ti:{}".format(num, integrity_errors))
                    num += 1
            except AssertionError as a:
                print(a)
                pass
    print('integrity_errors: {}'.format(integrity_errors))
    return num
