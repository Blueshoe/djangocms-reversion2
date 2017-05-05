=====================
Django-CMS Reversion2
=====================


**Django-CMS Reversion2** is a plugin for **Django CMS** which aims to provide a revision system for
**Django-CMS**.

As long as this plugin is under development it shall be used as git submodule.

Installation
============

* git submodule add <url> djangocms_reversion2
* git submodule update --init
* cd djangocms_reversion2/
* pip install -r requirements.txt
* add the "djangocms_reversion2" to INSTALLED_APPS
* python manage.py migrate

Documentation
=============

Please feel free to contribute and help us to improve **Django-CMS Reversion2**.

Features
--------

These are the core features of **Django-CMS Reversion2**:

* Based on **django-reversion**
* Revisions for page drafts in given language
* Reverting to any previous revision of page
* Auto-Revisions when reverting from unsaved drafts
* adds a trash to the page tree


ToDo's
------

No software is perfect, everyone's code sucks. Feel free to suggest, criticize and/or contribute.

**Proper Frontend/CMS-Admin Integration** - Currently, we unregister django-cms' default PageAdmin and register our own
PageAdmin. The overriding of PageAdmin appears necessary as it provides the only hook into Plugins being moved.

**Parametrised Plugin-Registration** - As of now, all CMSPlugin subclasses are registered with django-reversion without
additional parameters ('follows', etc.). That means, model instances referred to via foreign key relation by a Plugin
are currently not versioned and therefore not reverted. Such instances must still exist when reverting. Plugins having
reverse foreign key relations (as is the case in many-to-many relations) are handled particularly badly. The delteion of
the Plugin entails the deletion of the related model instance/m2m model instance.
