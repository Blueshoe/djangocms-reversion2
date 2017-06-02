# -*- coding: utf-8 -*-
from django.utils.functional import SimpleLazyObject

from cms.utils.compat.dj import MiddlewareMixin

from ..utils import get_draft_of_version_page, is_version_page


# Overwriting the middleware
# - because we can't resolve all permissions of a page when copying it to the hidden branch of the page tree
# -> therefore we check permissions in the CurrentPageMiddleware
# -> if access is allowed we have to give the user the necessary permissions

def get_page(request):
    from cms.appresolver import applications_page_check
    from cms.utils.page_resolver import get_page_from_request

    if not hasattr(request, '_current_page_cache'):
        request._current_page_cache = get_page_from_request(request)
        if not request._current_page_cache:
            # if this is in a apphook
            # find the page the apphook is attached to
            request._current_page_cache = applications_page_check(request)

    # check whether the page is under the ROOT_VERSION_PAGE (which means that it is a version)
    if request._current_page_cache:
        is_version = is_version_page(request._current_page_cache)
    else:
        is_version = False
    # TODO: skip for root users
    if is_version:
        # get the 'original' draft of the page.page_version
        original_draft = get_draft_of_version_page(request._current_page_cache)
        # now replace the pagepermission_set of the request's page by the 'original draft'
        request._current_page_cache.pagepermission_set = original_draft.pagepermission_set.get_queryset()

    return request._current_page_cache


class CurrentPageMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.current_page = SimpleLazyObject(lambda: get_page(request))
        return None
