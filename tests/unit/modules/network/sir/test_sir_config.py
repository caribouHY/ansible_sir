#
# (c) 2016 Red Hat Inc.
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
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# Make coding more python3-ish
from __future__ import absolute_import, division, print_function


__metaclass__ = type
from unittest.mock import MagicMock, patch

from ansible_collections.caribouhy.sir.plugins.cliconf.sir import Cliconf
from ansible_collections.caribouhy.sir.plugins.modules import sir_config
from ansible_collections.caribouhy.sir.tests.unit.modules.utils import set_module_args

from .sir_module import TestSirModule, load_fixture


class TestSirConfigModule(TestSirModule):
    module = sir_config

    def setUp(self):
        super(TestSirConfigModule, self).setUp()

        self.mock_get_config = patch(
            "ansible_collections.caribouhy.sir.plugins.modules.sir_config.get_config",
        )
        self.get_config = self.mock_get_config.start()

        self.mock_get_connection = patch(
            "ansible_collections.caribouhy.sir.plugins.modules.sir_config.get_connection",
        )
        self.get_connection = self.mock_get_connection.start()

        self.conn = self.get_connection()
        self.conn.edit_config = MagicMock()

        self.mock_run_commands = patch(
            "ansible_collections.caribouhy.sir.plugins.modules.sir_config.run_commands",
        )
        self.run_commands = self.mock_run_commands.start()

        self.mock_load_config = patch(
            "ansible_collections.caribouhy.sir.plugins.modules.sir_config.load_config",
        )
        self.load_config = self.mock_load_config.start()

        self.cliconf_obj = Cliconf(MagicMock())
        self.running_config = load_fixture("sir_config_config.cfg")

    def tearDown(self):
        super(TestSirConfigModule, self).tearDown()
        self.mock_get_config.stop()
        self.mock_run_commands.stop()
        self.mock_get_connection.stop()
        self.mock_load_config.stop()

    def load_fixtures(self, commands=None):
        config_file = "sir_config_config.cfg"
        self.get_config.return_value = load_fixture(config_file)
        self.get_connection.edit_config.return_value = None

    def test_sir_config_unchanged(self):
        src = load_fixture("sir_config_config.cfg")
        self.conn.get_diff = MagicMock(return_value=self.cliconf_obj.get_diff(src, src))
        set_module_args(dict(src=src))
        self.execute_module()

    def test_sir_config_src(self):
        src = load_fixture("sir_config_src.cfg")
        set_module_args(dict(src=src))
        self.conn.get_diff = MagicMock(
            return_value=self.cliconf_obj.get_diff(src, self.running_config),
        )
        commands = ["ether 1 1 description foo", "ether 2 1 vlan untag 3", "delete time auto"]
        self.execute_module(changed=True, commands=commands)

    def test_sir_config_backup(self):
        set_module_args(dict(backup=True))
        result = self.execute_module()
        self.assertIn("__backup__", result)
        self.assertEqual(result["__backup__"].endswith("\neof"), False)

    def test_sir_config_backup_eof(self):
        set_module_args(dict(backup=True, backup_options=dict(append_eof=True)))
        result = self.execute_module()
        self.assertIn("__backup__", result)
        self.assertEqual(result["__backup__"].endswith("\neof"), True)

    def test_sir_config_save_changed_true(self):
        src = load_fixture("sir_config_src.cfg")
        set_module_args(dict(src=src, save_when="changed"))
        commands = ["ether 1 1 description foo", "ether 2 1 vlan untag 3", "delete time auto"]
        self.conn.get_diff = MagicMock(
            return_value=self.cliconf_obj.get_diff(src, self.running_config),
        )
        self.execute_module(changed=True, commands=commands)
        self.assertEqual(self.run_commands.call_count, 1)
        self.assertEqual(self.get_config.call_count, 1)
        self.assertEqual(self.load_config.call_count, 1)
        args = self.run_commands.call_args[1]["commands"]
        self.assertIn("save", args)

    def test_sir_config_save_changed_false(self):
        set_module_args(dict(save_when="changed"))
        self.execute_module(changed=False)
        self.assertEqual(self.run_commands.call_count, 0)
        self.assertEqual(self.get_config.call_count, 0)
        self.assertEqual(self.load_config.call_count, 0)

    def test_sir_config_save_always(self):
        self.run_commands.return_value = "ether 2 1 description foo"
        set_module_args(dict(save_when="always"))
        self.execute_module(changed=True)
        self.assertEqual(self.run_commands.call_count, 1)
        self.assertEqual(self.get_config.call_count, 0)
        self.assertEqual(self.load_config.call_count, 0)
        args = self.run_commands.call_args[1]["commands"]
        self.assertIn("save", args)

    def test_sir_config_before(self):
        lines = ["ether 2 1 description foo"]
        set_module_args(dict(lines=lines, before=["test1", "test2"]))
        self.conn.get_diff = MagicMock(
            return_value=self.cliconf_obj.get_diff(
                "\n".join(lines),
                self.running_config,
            ),
        )
        commands = ["test1", "test2", "ether 2 1 description foo"]
        self.execute_module(changed=True, commands=commands, sort=False)

    def test_sir_config_after(self):
        lines = ["ether 2 1 description foo"]
        set_module_args(dict(lines=lines, after=["test1", "test2"]))
        self.conn.get_diff = MagicMock(
            return_value=self.cliconf_obj.get_diff(
                "\n".join(lines),
                self.running_config,
            ),
        )
        commands = ["ether 2 1 description foo", "test1", "test2"]
        self.execute_module(changed=True, commands=commands, sort=False)

    def test_sir_config_before_after_no_change(self):
        lines = ["ether 2 1 description test_string"]
        set_module_args(
            dict(lines=lines, before=["test1", "test2"], after=["test3", "test4"]),
        )
        self.conn.get_diff = MagicMock(
            return_value=self.cliconf_obj.get_diff(
                "\n".join(lines),
                self.running_config,
            ),
        )
        self.execute_module()

    def test_sir_config_config(self):
        config = "ether 2 1 description foo"
        lines = ["ether 2 1 description bar"]
        set_module_args(dict(lines=lines, config=config))
        self.conn.get_diff = MagicMock(
            return_value=self.cliconf_obj.get_diff("\n".join(lines), config),
        )
        commands = ["ether 2 1 description bar"]
        self.execute_module(changed=True, commands=commands)

    def test_sir_config_match_none(self):
        lines = ["ether 2 1 description foo"]
        set_module_args(dict(lines=lines, match="none"))
        self.conn.get_diff = MagicMock(
            return_value=self.cliconf_obj.get_diff(
                "\n".join(lines),
                self.running_config,
                diff_match="none",
            ),
        )
        self.execute_module(changed=True, commands=lines)

    def test_sir_config_src_and_lines_fails(self):
        args = dict(src="foo", lines="foo")
        set_module_args(args)
        self.execute_module(failed=True)
