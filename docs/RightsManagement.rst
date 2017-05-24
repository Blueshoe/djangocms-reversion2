A sketch for RightsManagement
=============================

For a simple collaboration workflow we need the following roles on every PageVersion
 - editors
 - grammar/spell checkers
 - admins
 - readers

UserStory for the workflow
--------------------------

1. Two editors decide to create different styles for one page
in order to let the readers choose the better one.
2. They create a PageVersion of the current page (the version before their competition)
3. Now they make a nonsense change and create a PageVersion for the first editor
4. ... and the same for the second editor
5. After writing they ask the grammar/spell checkers who have access to their versions to correct some
mistakes
6. Both editors create a new PageVersion with the corrected page content
7. They notify the user group 'readers' do give feedback
8. After modifying the pages according to the feedback the editors meet again
9. Now they can compare their final PageVersions to the current draft
(or even compare their PageVersions directly)
10. They decide which Version to use and make it the active PageVersion!

Requirements deduced from the UserStory
---------------------------------------

1. Parallel editing of PageVersions
2. Comparision of PageVersions
3. User groups
3.1 editors (also include the spell checkers)
3.2 admins
3.3 readers
4. Explicit sharing of a PageVersion?
