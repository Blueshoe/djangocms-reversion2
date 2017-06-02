Implementation
==============

We were trying to solve the page version history topic with a simple and pragmatic fix.
The old branch of this repository still contains our reversion2 with the json backend,
but that had some structural problems. And we had some new requirements:

Motivation
----------

1. Working on multiple drafts simultaneously
2. Not loosing constraints (any model connected to a plugin was a potential insecurity with the old backend)
3. Performance (serialization and de-serialization comes with performance cost) -> we prefer database cost
4. Avoiding the registration logic of the reversion backend for every models.py


Idea
----

1. When the user creates a new version of a page the draft is copied to a hidden root node in the page tree
2. This so called :code:`hidden_page` is linked to the :code:`PageVersion` model that keeps a reference to the :code:`visible draft`
3. There is always a PageVersion with the attribute :code:`primary draft`
4. The PageVersion is language specific so a rollback doesn't affect the translations of a page
5. The PageVersions are organized in an independent MP_Tree so they are chainable. This feature allows us to implement branching in a future step


