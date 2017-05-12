# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from itertools import chain

from cms.constants import PUBLISHER_STATE_DIRTY
from cms.utils import page as page_utils
from django.conf import settings

from cms import api, constants
from cms.exceptions import PublicIsUnmodifiable
from cms.extensions import extension_pool
from cms.models import Page, Placeholder, Title, menu_pool, copy_plugins_to


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
        'slug': page_utils.get_available_slug,
    },
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
    """
    if not page.publisher_is_draft:
        raise PublicIsUnmodifiable("revise page is not allowed for public pages")

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

    # copy the placeholders (and plugins on those placeholders!)
    for ph in Placeholder.objects.filter(page=origin_id).iterator():
        plugins = ph.get_plugins_list()
        try:
            # why might the placeholder already exist?
            ph = new_page.placeholders.get(slot=ph.slot)
        except Placeholder.DoesNotExist:
            ph = _copy_model(ph)
            page.placeholders.add(ph)
        if plugins:
            copy_plugins_to(plugins, ph, to_language=language)

    # TODO dig deep and find all implications of this and find out what do do when reversioning
    extension_pool.copy_extensions(Page.objects.get(pk=origin_id), new_page)

    new_page = new_page.move(version_page_root, pos="last-child")

    # invalidate the menu for this site
    menu_pool.clear(site_id=site.pk)
    return new_page


def revert_page(page_version, language):
    from djangocms_reversion2.models import PageVersion
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
    page_version.save()


def _copy_titles(source, target, language):
    """
    Copy all the titles to a new page (which must have a pk).
    :param target: The page where the new titles should be stored
    """
    #
    # source = Page()
    # target = Page()

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
        title.published = getattr(target_title, 'published', False)

        # dirty since we are overriding current draft
        title.publisher_state = PUBLISHER_STATE_DIRTY

        title.save()

    if old_titles:
        Title.objects.filter(id__in=old_titles.values()).delete()