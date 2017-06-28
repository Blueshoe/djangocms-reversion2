=====================
Django-CMS Reversion2
=====================

.. image:: https://readthedocs.org/projects/djangocms-reversion2/badge/?version=latest
    :target: http://djangocms-reversion2.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://travis-ci.org/Blueshoe/djangocms-reversion2.svg?branch=master
    :target: https://travis-ci.org/Blueshoe/djangocms-reversion2
    :alt: Code analysis status

UNSTABLE: We have tested this project locally but by now never used it in production.

Features
--------
These are the core features of Django-CMS Reversion2

Create versions of pages
........................

Create PageVersion: Revisions for page drafts in given language (only if changes were made see :code:`dirty` flag)

.. image:: https://raw.githubusercontent.com/Blueshoe/djangocms-reversion2/master/docs/sphinx/source/img/add_page_version.png

View differences between versions of a page
...........................................

Compare the current page with back-up versions.

.. image:: https://raw.githubusercontent.com/Blueshoe/djangocms-reversion2/master/docs/sphinx/source/img/diff_1.png


Revert a page to a version
..........................

Revert to PageVersion: Reverting to any previous revision of page

.. image:: https://raw.githubusercontent.com/Blueshoe/djangocms-reversion2/master/docs/sphinx/source/img/diff_sidebar.png

Create a version for all 'unversioned' pages
............................................

Trash bin: Moves deleted pages to a hidden PageRoot before really deleting it

.. image:: https://raw.githubusercontent.com/Blueshoe/djangocms-reversion2/master/docs/sphinx/source/img/batch_add.png

Multiple editors
................

**Experimental feature.** All page version can be edited.
Work on the hidden drafts of PageVersion in order to realize multi-editor workflow??

.. image:: https://raw.githubusercontent.com/Blueshoe/djangocms-reversion2/master/docs/sphinx/source/img/multi.png

Trash bin for pages
...................

Trash bin: Moves deleted pages to a hidden PageRoot before really deleting it

.. image:: https://raw.githubusercontent.com/Blueshoe/djangocms-reversion2/master/docs/sphinx/source/img/bucket.png

Permission system
.................

This plugin integrates with the django-cms permissions.

ToDos
-----

To be implemented (see Issues on Github `<https://github.com/Blueshoe/djangocms-reversion2/issues>`_)
 - Auto-Revisions when reverting from unsaved drafts
 - Integration with *divio/djangocms_moderation* once they publish a stable release
 - Build a multi-editor djangocms_toolbar and disable buttons that make unwanted changes

Disclaimer
----------

This is an experimental plugin.

No software is perfect, everyone's code sucks. Feel free to suggest, criticize and/or contribute.
