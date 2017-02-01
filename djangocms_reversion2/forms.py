# -*- coding: utf-8 -*-
from cms.utils import get_language_from_request
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _
from djangocms_reversion2.models import PageRevision
from djangocms_reversion2.page_revisions import PageRevisionCreator, PageRevisionError
from djangocms_reversion2.utils import get_page


class PageRevisionForm(forms.ModelForm):
    comment = forms.CharField(label=_('Comment'), help_text=_('Explain this snapshot'), widget=forms.Textarea)

    class Meta:
        model = PageRevision
        exclude = '__all__'

    def __init__(self, *args, **kwargs):
        super(PageRevisionForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial.update({'comment': self.instance.revision.comment})
        self.page_revision_creator = None
        self.revision = None

    def clean(self):
        cleaned_data = super(PageRevisionForm, self).clean()
        comment = force_text(cleaned_data.get('comment', ''))
        page_id = get_page(self.request)
        language = get_language_from_request(self.request)
        self.page_revision_creator = PageRevisionCreator(page_id, language, self.request, comment=comment)
        try:
            self.revision = self.page_revision_creator.revision
        except PageRevisionError as e:
            self.add_error(None, e.message)
        return cleaned_data

    def save(self, commit=True):
        super(PageRevisionForm, self).save(commit=False)
        return self.page_revision_creator.page_revision
