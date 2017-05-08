# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from djangocms_reversion2.models import PageVersion


class PageVersionForm(forms.ModelForm):

    class Meta:
        model = PageVersion
        fields = ['title', 'comment', 'draft']
        widgets = {
            'draft': forms.HiddenInput()
        }

    def save(self, commit=True):
        self.save_m2m = lambda: None
        data = self.cleaned_data
        comment = data.get('comment', '')
        title = data.get('title', '')
        draft = data['draft']
        # TODO detect case when editing version
        return PageVersion.create_version(draft, version_parent=None, comment=comment, title=title)

