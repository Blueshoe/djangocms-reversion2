# -*- coding: utf-8 -*-
from cms.api import create_page, add_plugin
from django.contrib.auth import get_user_model
from django.test.client import RequestFactory
from django.utils.timezone import now
from djangocms_text_ckeditor.cms_plugins import TextPlugin
from reversion.models import Revision

from djangocms_reversion2.diff import placeholder_html
from djangocms_reversion2.utils import revise_page
from djangocms_reversion2.models import PageVersion

from djangocms_reversion2.signals import make_page_version_dirty


class DR2BaseTestCase(object):
    COMMENT = 'Test comment'
    LANGUAGE = 'de'

    def setUp(self):
        self.user = self.get_superuser()
        self.page = self.create_page()
        self.request = self.get_request()
        self.add_text(self.page, content=u"initial")
        self.page_version = PageVersion.create_version(self.page.get_draft_object(), self.LANGUAGE,
                                                       version_parent=None, comment='', title='')

    def tearDown(self):
        self.page.delete()
        self.user.delete()

    def _create_user(self, username, is_staff=False, is_superuser=False, is_active=True):
        """
        Use this method to create users.
        """
        User = get_user_model()

        fields = dict(
            email=username + '@',
            last_login=now(),
            is_staff=is_staff,
            is_active=is_active,
            is_superuser=is_superuser
        )

        # Check for special case where email is used as username
        if User.USERNAME_FIELD != 'email':
            fields[User.USERNAME_FIELD] = username

        user = User(**fields)
        user.set_password(getattr(user, User.USERNAME_FIELD))
        user.save()

        return user

    def get_superuser(self):
        User = get_user_model()
        try:
            un_field = User.USERNAME_FIELD
            query = dict()
            query[un_field] = ("admin", "admin@blueshoe.de")[un_field == "email"]
            admin = User.objects.get(**query)
        except User.DoesNotExist:
            admin = self._create_user("admin", is_staff=True, is_superuser=True)
        return admin

    def create_page(self, name=None, template=None, language=None):
        name = name or 'home'
        template = template or 'template_1.html'
        language = language or 'de'
        return create_page(name, template, language, created_by=self.get_superuser().username)

    def add_text(self, page, n=1, content=u'example'):
        """
        Adds n text plugins to each placeholder in the page
        :param content:
        :param page:
        :param n:
        :return: the created plugin instances
        """
        plugins = []
        # put three text plugins in each placeholder
        for i, ph in enumerate(page.placeholders.all()):
            for language in page.get_languages():
                for j in xrange(n):
                    plugin = add_plugin(
                        ph, TextPlugin, language,
                        body=content
                    )
                    plugins.append(plugin)
        make_page_version_dirty(page, self.LANGUAGE)
        return plugins

    def get_html(self, page):
        html = ""
        for p in page.placeholders.iterator():
            html += self.get_current_html(p)
        return html

    def get_current_html(self, placeholder):
        return placeholder_html(placeholder, self.get_request(), self.LANGUAGE)

    def get_request(self):
        request_fac = RequestFactory()
        request = request_fac.get('/de/')
        request.user = self.user
        return request