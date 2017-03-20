# -*- coding: utf-8 -*-

# from djangocms_reversion2.page_revisions import unmark_page_revised
from djangocms_reversion2.models import PageMarker


def handle_cms_plugin_save(sender, instance, **kwargs):
    if instance.placeholder:
        PageMarker.unmark(instance.placeholder.page, instance.language)


def handle_page_save(sender, instance, **kwargs):
    pass


def handle_title_save(sender, instance, **kwargs):
    # PageMarker.objects.filter(page=instance.page, language=instance.language).delete()
    PageMarker.unmark(instance.page, instance.language)

