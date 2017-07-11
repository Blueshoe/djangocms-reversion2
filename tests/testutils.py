# -*- coding: utf-8 -*-
from cms.api import add_plugin
from djangocms_text_ckeditor.cms_plugins import TextPlugin

from djangocms_reversion2.diff import placeholder_html
from djangocms_reversion2.signals import make_page_version_dirty


def add_text(page, language, content, n=1):
    """
    Adds n text plugins to each placeholder in the page
    :param content:
    :param page:
    :param language:
    :param n:
    :return: the created plugin instances
    """
    plugins = []
    # put three text plugins in each placeholder
    for i, ph in enumerate(page.placeholders.all()):
        for language in page.get_languages():
            for j in range(n):
                plugin = add_plugin(ph, TextPlugin, language, body=content)
                plugins.append(plugin)
    make_page_version_dirty(page, language)
    return plugins


def get_html(request, language='en'):
    page = request.current_page
    html = ""
    for p in page.placeholders.iterator():
        html += placeholder_html(p, request, language)
    return html
