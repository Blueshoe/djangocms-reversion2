# -*- coding: utf-8 -*-
from django.db.models import signals


def make_page_version_dirty(page, language):
    pv = page.page_versions.filter(active=True, language=language)
    if pv.count() > 0:
        pv = pv.first()
        if not pv.dirty:
            pv.dirty = True
            pv.save()


def mark_title_dirty(sender, instance, **kwargs):
    page = instance.page
    language = instance.language
    make_page_version_dirty(page, language)


def handle_placeholder_change(**kwargs):
    language = kwargs.get('language')
    placeholder = kwargs.get('placeholder')
    target_placeholder = kwargs.get('target_placeholder', None)
    page = None
    if placeholder:
        page = placeholder.page
    elif target_placeholder:
        page = target_placeholder.page

    if page:
        make_page_version_dirty(page, language)


def handle_page_delete(sender, instance, **kwargs):
    page = instance

    for pv in page.page_versions.iterator():
        pv.hidden_page.delete()
        pv.delete()




def connect_all_plugins():
    from cms.signals import post_placeholder_operation
    post_placeholder_operation.connect(handle_placeholder_change, dispatch_uid='reversion2_placeholder')
    signals.post_save.connect(mark_title_dirty, sender='cms.Title', dispatch_uid='reversion2_title')
    signals.pre_delete.connect(handle_page_delete, sender='cms.Page', dispatch_uid='reversion2_page')

