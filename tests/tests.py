from cms.api import create_page
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from djangocms_helper.base_test import BaseTestCase

from djangocms_reversion2.page_revisions import AUTO_REVISION_COMMENT
from pytest import raises


from djangocms_reversion2.models import PageVersion

from djangocms_reversion2.utils import revert_page

from djangocms_reversion2.signals import make_page_version_dirty

import testutils


class PageRevisionCreateTestCase(BaseTestCase):

    def test_a_revise_page(self):
        language = 'en'
        page = create_page(title='test_a_revise_page', template='page.html', language=language)
        testutils.add_text(page, language, content=u"initial")
        page_version = PageVersion.create_version(page.get_draft_object(), language,
                                                  version_parent=None, comment='', title='')
        self.assertIsNotNone(page_version, msg='PageVersion creation failed')

    def test_b_revise_page(self):
        language = 'en'
        draft = create_page(title='next', template='page.html', language=language).get_draft_object()
        # create initial version
        pv = PageVersion.create_version(draft, language, version_parent=None, comment='next', title='')

        # we have a revised page containing the text 'initial' and add the text 'next'
        testutils.add_text(draft, language, content=u"next")
        html = testutils.get_html(request=self.get_page_request(draft, self.user))
        self.assertIn('next', html, msg='could not add content')

        # we check that the the revision does not contain 'next'
        draft.refresh_from_db()
        html = testutils.get_html(self.get_page_request(draft.page_versions.last().hidden_page, self.user))
        self.assertNotIn('next', html, msg='content should not be added to an old revision')

        try:
            # now we create a new version
            pv = PageVersion.create_version(draft, language, version_parent=None, comment='next', title='')
        except AssertionError:
            self.fail('Expected the page to be dirty, but it\'s clean')

        # this version should contain the new text
        draft.refresh_from_db()
        html = testutils.get_html(request=self.get_page_request(pv.hidden_page, self.user))
        self.assertIn('next', html, msg='new content is not in the latest version')

        # now we revert to the old date
        revert_page(draft.page_versions.first(), language)
        html = testutils.get_html(request=self.get_page_request(draft, self.user))
        self.assertNotIn('next', html, msg='new content is still in the page')

    # def test_b_revise_page_fields(self):
    #     LANGUAGE = 'en'
    #     pr = PageRevision.objects.get(page_id=self.page.id, language=LANGUAGE)
    #     self.assertEqual(pr.revision.comment, self.COMMENT)
    #     self.assertEqual(pr.revision.user, self.user)
    #     self.assertEqual(pr.language, self.LANGUAGE)
    #
    # def test_c_revise_page_page_is_revised(self):
    #     self.assertTrue(is_revised(self.page, self.LANGUAGE))
    #     self.assertTrue(PageMarker.objects.filter(language=self.LANGUAGE, page=self.page).exists())
    #     self.assertEqual(PageMarker.objects.get(language=self.LANGUAGE, page=self.page).page_revision, self.page_revision)
    #
    # def test_d_revise_page_revise_again_unsuccessful(self):
    #     new_revision = revise_page(self.page, language=self.LANGUAGE)
    #     self.assertEqual(new_revision, None)
    #     self.assertEqual(1, self.page.pagerevision_set.count())
#
#
# class PageRevisionUnmarkPageTestCase(DR2BaseTestCase, TestCase):
#     def setUp(self):
#         super(PageRevisionUnmarkPageTestCase, self).setUp()
#         self.added_plugins = self.add_text(self.page, n=1)
#
#     def test_a_page_unmarked(self):
#         self.assertFalse(is_revised(self.page, self.LANGUAGE))
#         self.assertFalse(PageMarker.objects.filter(language=self.LANGUAGE, page=self.page).exists())
#
#
# class PageRevisionRevertTestCase(DR2BaseTestCase, TestCase):
#     def setUp(self):
#         super(PageRevisionRevertTestCase, self).setUp()
#         self.added_plugins = self.add_text(self.page, n=1)
#         self.page_marker = revert_page(self.page_revision, self.request)
#         self.initial_html = {
#             ph.slot: self.get_current_html(ph) for ph in self.page.placeholders.all()
#         }
#
#     def test_a_revert_deletion(self):
#         print Text.objects.all()
#         for pl in self.added_plugins:
#             try:
#                 pl.refresh_from_db()
#                 self.fail()
#             except ObjectDoesNotExist:
#                 pass
#
#     def test_b_revert_auto_revision(self):
#         self.assertEqual(2, self.page.pagerevision_set.count())
#         auto_revision = self.page.pagerevision_set.latest('pk')
#         self.assertEqual(auto_revision.revision.comment, AUTO_REVISION_COMMENT)
#
#     def test_c_revert_correct_html(self):
#         for placeholder in self.page.placeholders.all():
#             slot = placeholder.slot
#             html = self.get_current_html(placeholder)
#             self.assertEqual(self.initial_html[slot], html, slot)
#
