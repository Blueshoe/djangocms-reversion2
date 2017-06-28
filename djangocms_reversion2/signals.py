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
    # deleting a real page will delete all of its hidden versions
    page = instance

    for pv in page.page_versions.iterator():
        pv.hidden_page.delete()
        pv.delete()


def delete_hidden_page(sender, **kwargs):
    # deleting a PageVersion deletes its hidden page in the PageTree
    # This signal handler deletes the hidden page associated to a PageVersion
    # (reverse to on_delete=models.CASCADE)
    # Problem was that an infinite loop can be originated
    # if kwargs['instance'] and kwargs['instance'].hidden_page:
    #     hidden_page = kwargs['instance'].hidden_page
    #     try:
    #         hidden_page.delete()
    #     except Exception as e:
    #         print(e)
    pass


def connect_all_plugins():
    from cms.signals import post_placeholder_operation
    post_placeholder_operation.connect(handle_placeholder_change, dispatch_uid='reversion2_placeholder')
    signals.post_save.connect(mark_title_dirty, sender='cms.Title', dispatch_uid='reversion2_title')
    signals.pre_delete.connect(handle_page_delete, sender='cms.Page', dispatch_uid='reversion2_page')
    signals.pre_delete.connect(delete_hidden_page, sender='djangocms_reversion2.PageVersion',
                                dispatch_uid='reversion2_page_version')

