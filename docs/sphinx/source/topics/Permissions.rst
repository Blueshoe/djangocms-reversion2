Permissions
===========

View
----
If a user can view a page he can view its page versions.


Creation
--------
A user can create a page version for pages for which he has the cms.page.can_change_page.
An admin can create a page if he has cms.page_global_permission.can_change_page_global_permission

cms.utils.page_permissions: user_can_change_page

Batch-Creation
--------------
Only superusers are allowed to use the batch creation.

Edit
----
A user can edit page versions of pages that he is allowed to edit.
TODO: see copy pagepermissions on copy (see https://github.com/Blueshoe/djangocms-reversion2/issues/32)

Deletion
--------
*Attention:* A user mustn't delete own page versions because it might harm the page version tree.
TODO: So far page versions cannot be deleted at all ;)

An admin can delete page versions if he has the cms.page_global_permission.can_delete_page_global_permission

Rollback
--------
A user can roll back a page to a page version if he has the permission to publish the page (cms.page.can_publish_page)
An admin can rollback a page if he has any global page permission
(cms.page_global_permission.can_change_page_global_permission)


How the check works
-------------------

.. code-block:: python

    # check if the current user is allowed to revert the page by checking the publish permission
    user = get_current_user()
    if not user_can_publish_page(user, page_version.draft):
        messages.error(request, _('Missing permission to publish this page which is necessary for the rollback'))
        prev = request.META.get('HTTP_REFERER')
        if prev:
            return redirect(prev)
        else:
            raise Http404
