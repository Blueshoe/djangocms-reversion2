# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0016_auto_20160608_1535'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageVersion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path', models.CharField(unique=True, max_length=255)),
                ('depth', models.PositiveIntegerField()),
                ('numchild', models.PositiveIntegerField(default=0)),
                ('comment', models.TextField(help_text='Particular information concerning this Version', verbose_name='Comment', blank=True)),
                ('title', models.CharField(max_length=63, verbose_name='Name', blank=True)),
                ('active', models.BooleanField(default=False, help_text='This the active version of current draft. There can be only one such version per Page version tree.', verbose_name='Active')),
                ('draft', models.ForeignKey(related_name='page_versions', verbose_name='Draft', to='cms.Page', help_text='Current active draft.')),
                ('hidden_page', models.OneToOneField(related_name='page_version', verbose_name='Hidden Page', to='cms.Page', help_text='This Page object holds the versioned contents of this PageVersion.')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
