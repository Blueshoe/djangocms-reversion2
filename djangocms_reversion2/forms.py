# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.conf import settings

from djangocms_reversion2.models import PageVersion


class PageVersionForm(forms.ModelForm):

    class Meta:
        model = PageVersion
        fields = ['title', 'comment', 'draft', 'language']
        widgets = {
            'draft': forms.HiddenInput(),
            'language': forms.HiddenInput()
        }

    def save(self, commit=True):
        self.save_m2m = lambda: None
        data = self.cleaned_data
        comment = data.get('comment', '')
        title = data.get('title', '')
        draft = data['draft']
        language = data.get('language', '')
        # TODO detect case when editing version
        return PageVersion.create_version(draft, language, version_parent=None, comment=comment, title=title)

