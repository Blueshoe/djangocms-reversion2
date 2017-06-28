# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_reversion2', '0002_pageversion_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='pageversion',
            name='dirty',
            field=models.BooleanField(default=False, help_text='Only new PageVersions are not dirty of if a page has been reverted to a PageVersion.', verbose_name='Dirty'),
        ),
    ]
