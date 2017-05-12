# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_reversion2', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pageversion',
            name='language',
            field=models.CharField(max_length=20, verbose_name='Language', blank=True),
        ),
    ]
