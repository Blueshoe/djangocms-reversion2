.. djangocms_reversion2 documentation master file, created by
   sphinx-quickstart on Wed May 24 16:48:47 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to djangocms_reversion2's documentation!
================================================

**UNSTABLE**

**Django-CMS Reversion2** is a plugin for **Django CMS** which aims to provide a revision system for
**Django-CMS**.

These are the **core features** of Django-CMS Reversion2:
 - **Create PageVersion:** Revisions for page drafts in given language (only if changes were made see :code:`dirty` flag)
 - **Revert to PageVersion:** Reverting to any previous revision of page
 - **Trash-Bin:** Moves deleted pages to a hidden PageRoot before really deleting it
 - **Batch-mode:** Adds reversion for every page (only for superusers)
 - **Page Permissions**: Integrates with djangocms' pagepermissions
 - **Multi-editor**: Work on the hidden drafts of PageVersion in order to realize multi-editor workflow

To be implemented (see Issues on Github `<https://github.com/Blueshoe/djangocms-reversion2/issues>`_)
 - Auto-Revisions when reverting from unsaved drafts
 - Integration with *divio/djangocms_moderation* once they publish a stable release
 - Build a multi-editor djangocms_toolbar and disable buttons that make unwanted changes

Contents
--------

.. toctree::
   :maxdepth: 2

   topics/Motivation
   topics/Installation
   topics/Trees
   topics/Permissions

Disclaimer
----------

No software is perfect, everyone's code sucks. Feel free to suggest, criticize and/or contribute.

**Proper Frontend/CMS-Admin Integration** - Currently, we unregister django-cms' default PageAdmin and register our own
PageAdmin. The overriding of PageAdmin appears necessary as it provides the only hook into Plugins being moved.



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
