# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_reversion2', '0003_pageversion_dirty'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pageversion',
            options={'default_permissions': ('add', 'change', 'delete')},
        ),
        migrations.AddField(
            model_name='pageversion',
            name='owner',
            field=models.CharField(default='script', verbose_name='owner', max_length=255, editable=False),
        ),
    ]
