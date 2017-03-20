# -*- coding: utf-8 -*-

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.encoding import smart_text as u
from django.utils.translation import ugettext_lazy as _

# Create your models here.


@python_2_unicode_compatible
class PageMarker(models.Model):
    # marks a page as captured in a revision. Markers are deleted as soon as a plugin in the page is saved.
    page = models.ForeignKey('cms.Page', on_delete=models.CASCADE, verbose_name=_('page'), blank=False,
                             editable=False, related_name='page_markers')
    page_revision = models.OneToOneField('djangocms_reversion2.PageRevision', on_delete=models.CASCADE,
                                         verbose_name=_('page revision'), related_name='page_marker')
    language = models.CharField(_('language'), max_length=15, blank=False, db_index=True, editable=False)

    @classmethod
    def unmark(cls, page, language=None):
        delete_markers = cls.objects.filter(page=page)
        if language:
            delete_markers = delete_markers.filter(language=language)
        delete_markers.delete()

    def __str__(self):
        return u'Marker: Page #{page}'.format(page=self.page_id)

    class Meta:
        app_label = "djangocms_reversion2"
        unique_together = (('language', 'page'),)


@python_2_unicode_compatible
class PageRevision(models.Model):
    language = models.CharField(_('language'), max_length=15, blank=False, db_index=True, editable=False)
    page = models.ForeignKey('cms.Page', on_delete=models.CASCADE, verbose_name=_('page'), blank=False, editable=False)
    revision = models.OneToOneField('reversion.Revision', on_delete=models.CASCADE, verbose_name=_('revision'),
                                    blank=False, editable=False)

    class Meta:
        app_label = "djangocms_reversion2"
        ordering = ("-pk",)
        unique_together = (('language', 'page', 'revision'),)

    def __str__(self):
        return 'PageRevision #{pk}'.format(pk=self.pk)


@python_2_unicode_compatible
class HtmlContent(models.Model):
    body = models.TextField(_('Content'), unique=True, editable=False)

    class Meta:
        app_label = "djangocms_reversion2"
        verbose_name = _('HTML content')
        verbose_name_plural = _('HTML contents')

    def __str__(self):
        return u(self.body[:50]) if len(self.body) < 50 else u(self.body[:50]) + u'...'

    def save(self, **kwargs):
        if self.pk:
            raise Exception("Don't edit an existing instance! Html content might be shared between page revisions.")
        super(HtmlContent, self).save(**kwargs)


@python_2_unicode_compatible
class PageRevisionPlaceholderContent(models.Model):
    page_revision = models.ForeignKey('PageRevision', on_delete=models.CASCADE, related_name='placeholder_contents',
                                      related_query_name='placeholder_content', verbose_name=_('Page revision'))
    placeholder = models.ForeignKey('cms.Placeholder', on_delete=models.CASCADE, related_name='page_revision_contents',
                                    related_query_name='page_revision_content', verbose_name='Placeholder')
    html_content = models.ForeignKey('HtmlContent', on_delete=models.CASCADE, related_name='page_revision_placeholders',
                                     related_query_name='page_revision_placeholder', verbose_name=_('HTML Content'))

    class Meta:
        app_label = "djangocms_reversion2"
        verbose_name = _('Page revision placeholder content')
        verbose_name_plural = _('Page revision placeholder contents')
        unique_together = (('page_revision', 'placeholder'),)

    def __str__(self):
        return u'PageRevision #{pr_id} - Placeholder #{ph_id}: {content}'.format(
            pr_id=self.page_revision_id, ph_id=self.placeholder_id, content=u(self.html_content))
