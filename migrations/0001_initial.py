# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0016_auto_20160608_1535'),
        ('reversion', '0001_squashed_0004_auto_20160611_1202'),
    ]

    operations = [
        migrations.CreateModel(
            name='HtmlContent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('body', models.TextField(verbose_name='Content', unique=True, editable=False)),
            ],
            options={
                'verbose_name': 'HTML content',
                'verbose_name_plural': 'HTML contents',
            },
        ),
        migrations.CreateModel(
            name='PageMarker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(verbose_name='language', max_length=15, editable=False, db_index=True)),
                ('page', models.ForeignKey(related_name='page_markers', editable=False, to='cms.Page', verbose_name='page')),
            ],
        ),
        migrations.CreateModel(
            name='PageRevision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(verbose_name='language', max_length=15, editable=False, db_index=True)),
                ('page', models.ForeignKey(editable=False, to='cms.Page', verbose_name='page')),
                ('revision', models.OneToOneField(editable=False, to='reversion.Revision', verbose_name='revision')),
            ],
            options={
                'ordering': ('-pk',),
            },
        ),
        migrations.CreateModel(
            name='PageRevisionPlaceholderContent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('html_content', models.ForeignKey(related_query_name=b'page_revision_placeholder', related_name='page_revision_placeholders', verbose_name='HTML Content', to='djangocms_reversion2.HtmlContent')),
                ('page_revision', models.ForeignKey(related_query_name=b'placeholder_content', related_name='placeholder_contents', verbose_name='Page revision', to='djangocms_reversion2.PageRevision')),
                ('placeholder', models.ForeignKey(related_query_name=b'page_revision_content', related_name='page_revision_contents', verbose_name=b'Placeholder', to='cms.Placeholder')),
            ],
            options={
                'verbose_name': 'Page revision placeholder content',
                'verbose_name_plural': 'Page revision placeholder contents',
            },
        ),
        migrations.AddField(
            model_name='pagemarker',
            name='page_revision',
            field=models.OneToOneField(related_name='page_marker', verbose_name='page revision', to='djangocms_reversion2.PageRevision'),
        ),
        migrations.AlterUniqueTogether(
            name='pagerevisionplaceholdercontent',
            unique_together=set([('page_revision', 'placeholder')]),
        ),
        migrations.AlterUniqueTogether(
            name='pagerevision',
            unique_together=set([('language', 'page', 'revision')]),
        ),
        migrations.AlterUniqueTogether(
            name='pagemarker',
            unique_together=set([('language', 'page')]),
        ),
    ]
