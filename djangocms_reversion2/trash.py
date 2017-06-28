# def view_revision(self, request, **kwargs):
    #     # render a page for a popup in an old revision
    #     revision_pk = kwargs.pop('revision_pk')
    #     page_revision = PageRevision.objects.get(id=revision_pk)
    #     # get the rendered_placeholders which are persisted as html strings
    #     prc = PageRevisionComparator(page_revision, request=request)
    #     rendered_placeholders = prc.rendered_placeholders
    #
    #     context = SekizaiContext({
    #         'current_template': page_revision.page.get_template(),
    #         'rendered_placeholders': rendered_placeholders,
    #         'page_revision': page_revision,
    #         'is_popup': True,
    #         'request': request,
    #     })
    #     return render(request, self.view_revision_template, context=context)
    #
    # def download_audit_trail(self, request):
    #     # show view where the user can select the desired download params
    #     # self.set_page_lang(request)
    #     return TemplateResponse(request, 'admin/download_audit_trail.html',
    #                             {'p_id': request.GET.get('page_id'), 'lang': request.GET.get('language')}
    #                             )

    # def download_audit_trail_xlsx(self, request, **kwargs):
    #     # download the audit trail as xlsx
    #     # self.set_page_lang(request)  , language=get_language_from_request(request)
    #     page_id = request.GET.get('page_id')
    #     language = request.GET.get('language')
    #     request.current_page = Page.objects.get(id=page_id)
    #     report = exporter.ReportXLSXFormatter()
    #     return report.get_download_response(request, self.get_queryset(request), language=language)

    # def revert(self, r        equest, ** kwargs):
        #     # revert page to revision
        #     pk = kwargs.pop('pk')
        #     language = request.GET.get('language')
        #     page_revision = PageRevision.objects.get(id=pk)
        #
        #     if not revert_page(page_revision, request):
        #         messages.info(request, u'Page is already in this revision!')
        #         prev = request.META.get('HTTP_REFERER')
        #         if prev:
        #             return redirect(prev)
        #         return self.changelist_view(request, **kwargs)
        #
        #     # create a new revision if reverted to keep history correct
        #     # therefore mark a placeholder as dirty
        #     # TODO: in case of no placeholder?
        #     # page_revision.page.placeholders.first().mark_as_dirty(language)
        #     # creator = PageRevisionCreator(page_revision.page.pk, language, request, request.user,
        #     # ugettext(u'Restored') + ' ' + '#' + str(page_revision.pk))
        #     # creator.create_page_revision()
        #
        #
        # messages.info(request, _(u'You have succesfully reverted to {rev}').format(rev=page_revision))
        # return self.render_close_frame()

    # def diff(self, request, **kwargs):
    #     # deprecated diff view (used in the PageRevisionForm)
    #     # deprecated because it was only able to show an html code difference
    #     # which compares a revision to a page
    #     # -> REPLACED BY diff-view
    #     pk = kwargs.pop('pk')
    #     page_revision = PageRevision.objects.get(id=pk)
    #
    #     prc = PageRevisionComparator(page_revision, request=request)
    #     slot_html = {slot: revert_escape(html) for slot, html in prc.slot_html.items() if slot in prc.changed_slots}
    #
    #     if not slot_html:
    #         messages.info(request, _(u'No diff between revision and current page detected'))
    #         return self.changelist_view(request, **kwargs)
    #
    #     context = SekizaiContext({
    #         'title': _(u'Diff current page and page revision #{pk}').format(pk=pk),
    #         'slot_html': slot_html,
    #         'is_popup': True,
    #         'page_revision_id': page_revision.pk,
    #         'request': request
    #     })
    #     return render(request, self.diff_template, context=context)