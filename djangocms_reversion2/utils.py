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


VERSION_ROOT_TITLE = '.~VERSION_ROOT_TITLE'

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


def revise_page(page):
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
    for title in Title.objects.filter(page=origin_id).iterator():
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
            copy_plugins_to(plugins, ph)

    # TODO dig deep and find all implications of this and find out what do do when reversioning
    extension_pool.copy_extensions(Page.objects.get(pk=origin_id), new_page)

    new_page = new_page.move(version_page_root, pos="last-child")

    # invalidate the menu for this site
    menu_pool.clear(site_id=site.pk)
    return new_page


# def revert_page(page_version):
#     # copy all relevant attributes from hidden_page to draft
#     source = page_version.hidden_page
#     target = page_version.draft
#     source = Page()
#     target = Page()
#     source._copy_attributes(target)
#     for language in source.get_languages():
#         source._copy_titles(target, language)
#
# def _copy_titles(source, target, language, published):
#     """
#     Copy all the titles to a new page (which must have a pk).
#     :param target: The page where the new titles should be stored
#     """
#
#     source = Page()
#     target = Page()
#
#     assert source.publisher_is_draft
#     assert target.publisher_is_draft
#
#     old_titles = dict(target.title_set.filter(language=language).values_list('language', 'pk'))
#     for title in source.title_set.filter(language=language):
#         old_pk = title.pk
#         # If an old title exists, overwrite. Otherwise create new
#         target_pk = old_titles.pop(title.language, None)
#         title.pk = target_pk
#
#         # this is the previous title of target, we will keep some of this values
#         target_title = Title.objects.get(pk=target_pk) if target_pk else None
#
#         title.page = target
#         title.publisher_is_draft = True
#         title.publisher_public_id = target_title.publisher_public_id if target_title else None
#         title.publisher_state = PUBLISHER_STATE_DIRTY
#         title.published = published
#         title._publisher_keep_state = True
#         title.save()
#
#         old_title = Title.objects.get(pk=old_pk)
#         old_title.publisher_public = title
#         old_title.publisher_state = title.publisher_state
#         old_title.published = True
#         old_title._publisher_keep_state = True
#         old_title.save()
#         if hasattr(source, 'title_cache'):
#             source.title_cache[language] = old_title
#     if old_titles:
#         Title.objects.filter(id__in=old_titles.values()).delete()