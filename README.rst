=====================
Django-CMS Reversion2
=====================

.. image:: https://readthedocs.org/projects/djangocms-reversion2/badge/?version=latest
    :target: http://djangocms-reversion2.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

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

ToDo's
------

No software is perfect, everyone's code sucks. Feel free to suggest, criticize and/or contribute.