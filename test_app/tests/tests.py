from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from djangocms_text_ckeditor.models import Text

from djangocms_reversion2.page_revisions import AUTO_REVISION_COMMENT
from test_app.tests.testutils import DR2BaseTestCase


class PageRevisionCreateTestCase(DR2BaseTestCase, TestCase):
    COMMENT = 'Test comment'
    LANGUAGE = 'de'

    def test_a_revise_page(self):
        try:
            assert self.page_revision is not None
        except AssertionError:
            self.fail('PageVersion creation failed')
#
#     def test_b_revise_page_fields(self):
#         pr = PageRevision.objects.get(page_id=self.page.id, language=self.LANGUAGE)
#         self.assertEqual(pr.revision.comment, self.COMMENT)
#         self.assertEqual(pr.revision.user, self.user)
#         self.assertEqual(pr.language, self.LANGUAGE)
#
#     def test_c_revise_page_page_is_revised(self):
#         self.assertTrue(is_revised(self.page, self.LANGUAGE))
#         self.assertTrue(PageMarker.objects.filter(language=self.LANGUAGE, page=self.page).exists())
#         self.assertEqual(PageMarker.objects.get(language=self.LANGUAGE, page=self.page).page_revision, self.page_revision)
#
#     def test_d_revise_page_revise_again_unsuccessful(self):
#         new_revision = revise_page(self.page, language=self.LANGUAGE)
#         self.assertEqual(new_revision, None)
#         self.assertEqual(1, self.page.pagerevision_set.count())
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
