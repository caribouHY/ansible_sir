=============================================================
Si-R Collection Release Notes
=============================================================

.. contents:: Topics

v1.2.1
======

Bugfixes
--------

- Fix action module routing.


v1.2.0
======

Minor Changes
-------------

- sir_config - Add support for append `eof` to the end of backup configuration.
- sir_config - Add support for `commit try` command.

v1.1.0
======

New Modules
-----------

- sir_config - Module to manage configuration sections.
- sir_ping - Tests reachability using ping from Si-R router.

Bugfixes
--------

- terminal - support teminal timestamp and fix become.

v1.0.0
======

New Plugins
-----------

Cliconf
~~~~~~~

- sir - Use sir cliconf to run command on Si-R devices.

New Modules
-----------

- sir_command - Module to run commands on Si-R devices.