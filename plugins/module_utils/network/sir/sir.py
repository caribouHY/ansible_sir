# (c) 2017 Red Hat Inc.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <https://www.gnu.org/licenses/gpl-3.0.txt>.
#
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from ansible.module_utils._text import to_text
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    to_list,
)
from ansible.module_utils.connection import Connection, ConnectionError

_DEVICE_CONFIGS = {}


def get_connection(module):
    if hasattr(module, "_sir_connection"):
        return module._sir_connection

    capabilities = get_capabilities(module)
    network_api = capabilities.get("network_api")
    if network_api == "cliconf":
        module._sir_connection = Connection(module._socket_path)
    else:
        module.fail_json(msg="Invalid connection type %s" % network_api)

    return module._sir_connection


def get_capabilities(module):
    if hasattr(module, "_sir_capabilities"):
        return module._sir_capabilities
    try:
        capabilities = Connection(module._socket_path).get_capabilities()
    except ConnectionError as exc:
        module.fail_json(msg=to_text(exc, errors="surrogate_then_replace"))
    module._sir_capabilities = json.loads(capabilities)
    return module._sir_capabilities


def get_config(module, flags=None):
    flags = to_list(flags)

    section_filter = False
    if flags and "section" in flags[-1]:
        section_filter = True

    flag_str = " ".join(flags)

    try:
        return _DEVICE_CONFIGS[flag_str]
    except KeyError:
        connection = get_connection(module)
        try:
            out = connection.get_config(flags=flags)
        except ConnectionError as exc:
            if section_filter:
                module.warn("section %s" % section_filter)
                out = get_config(module, flags=flags[:-1])
            else:
                module.fail_json(msg=to_text(exc, errors="surrogate_then_replace"))
        cfg = to_text(out, errors="surrogate_then_replace").strip()
        _DEVICE_CONFIGS[flag_str] = cfg
        return cfg


def get_defaults_flag(module):
    connection = get_connection(module)
    try:
        out = connection.get_defaults_flag()
    except ConnectionError as exc:
        module.fail_json(msg=to_text(exc, errors="surrogate_then_replace"))
    return to_text(out, errors="surrogate_then_replace").strip()


def run_commands(module, commands, check_rc=True):
    connection = get_connection(module)
    try:
        return connection.run_commands(commands=commands, check_rc=check_rc)
    except ConnectionError as exc:
        module.fail_json(msg=to_text(exc))


def load_config(module, commands, commit=False, commit_timer=None):
    connection = get_connection(module)

    try:
        resp = connection.edit_config(candidate=commands, commit=commit, commit_timer=commit_timer)
        return resp.get("response")
    except ConnectionError as exc:
        module.fail_json(msg=to_text(exc))
