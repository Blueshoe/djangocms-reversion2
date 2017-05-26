Permissions
===========

View
----
If a user can view a page he can view its page versions.

.. code-block:: python

   user = get_current_user()
   if not has_page_permission(user, page_version.draft, 'view_page'):
      prev = request.META.get('HTTP_REFERER')
      messages.error(request, _('Missing permission to view this page.'))
         if prev:
            return redirect(prev)
         else:
            raise Http404

Creation
--------
A user can create a page version for pages for which he has the cms.page.can_change_page.
An admin can create a page if he has cms.page_global_permission.can_change_page_global_permission

Edit
----
A user can edit own page versions. (if the creator of the page version is the user)
An admin can edit page versions if he has cms.page_global_permission.can_change_page_global_permission

Deletion
--------
*Attention:* A user mustn't delete own page versions because it might harm the page version tree.

An admin can delete page versions if he has the cms.page_global_permission.can_delete_page_global_permission

Rollback
--------
A user can roll back a page to a page version if he has the permission to publish the page (cms.page.can_publish_page)
An admin can rollback a page if he has any global page permission
(cms.page_global_permission.can_change_page_global_permission)



