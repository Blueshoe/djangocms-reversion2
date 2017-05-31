Permissions
===========

That's how we need it?
 - users that edit a page can't change it but make a new branch where they work on and afterwards make a pull request to
   the page owner

That's how we want it:
 1) The external person creates a new page version from the page **He has to be able to view the page!**
 2) external can work on his page separately
 3) either ask an admin to 'revert' to this page version or use the djangocms-moderation plugin

Integration with djangocms-moderation
-------------------------------------

This plugin replaces the "publish button" with a "moderation request button".
Then a "moderation workflow" is attached to the page. Now the edit functions of the page are blocked until the workflow
is either rejected or approved.

How we could use this:
......................

1) We still hide the toolbar in the "edit page version" mode but add another button that triggers a special workflow
2) When that workflow has finished
 3) Here comes the tricky part with djangocms-moderation -> they are building a workflow for approval of page publishing
        -> we would like to use this in future releases. This might look like this:
                - the external starts a new moderation request on the edited hidden_page
                - we use @receiver(post_obj_operation) signal handler to catch the end of the workflow
                - instead of clicking the publish button on the hidden_page (we make a rollback of the connected draft)

**You have to add CMS_PERMISSIONS = True to your settings.py!**

Implementation of the current permission system
===============================================

We make use of the cms page permissions because they are already there and we don't get any inconsistencies with custom
permissions.
Every page has a :code:`pagepermission_set`. If a new page version is created all of these permissions have to be
copied to the hidden_page of the page version.

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


Example: How the check works
----------------------------

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
