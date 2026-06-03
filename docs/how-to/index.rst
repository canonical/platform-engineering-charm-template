.. meta::
   :description: How-to guides for operating the __charm_name__ charm, including basic operations, upgrades, and development. 

.. _how_to_index:

How-to guides
=============

.. TODO: Update the name of the charm!
         The following subsections are examples and don't need to be followed exactly.
         Define themes and subsections based on the charm's unique needs and features.
         Avoid subsections that only apply to a single page (creating an "orphan").
         Select subsections where 2 or more pages apply.

         Provide 1-2 sentence introductions for each subsection.
         Avoid meta-documentation that describes the documentation itself
         (e.g., "The following guides document..."). Try to focus explanatory
         text on the purpose or value of the guides listed in the section.

         More examples of subsections: Initial setup, Security


Manage the full operations lifecycle of the __charm_name__ charm, from initial deployment
through production maintenance.
Each guide assumes that you've already deployed the charm with Juju.

.. vale Canonical.013-Spell-out-numbers-below-10 = NO
.. vale Canonical.500-Repeated-words = NO

Basic operations
----------------

Once you've finished setting up the charm, now you can perform a number
of actions with your deployment. These guides provide instructions on
basic operations you can complete with the charm.

.. toctree::
    :hidden:
    :maxdepth: 1

    Integrate with COS <integrate-with-cos>

Update and refresh
------------------

Backups, redeployments, and upgrades ensure the
__charm_name__ charm stays current and benefits from new features
and capabilities.

.. toctree::
    :hidden:
    :maxdepth: 1

    Back up and restore <back-up-restore>
    Redeploy <redeploy>
    Upgrade <upgrade>

Development
-----------

These guides can help you with troubleshooting and contributing to the project.

.. toctree::
    :hidden:
    :maxdepth: 1

    Use Terraform <terraform>
    Troubleshoot <troubleshoot>
    Contribute <contribute>