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

from unittest.mock import patch

from ansible_collections.caribouhy.sir.plugins.modules import sir_command
from ansible_collections.caribouhy.sir.tests.unit.modules.utils import set_module_args

from .sir_module import TestSirModule, load_fixture


class TestSirCommandModule(TestSirModule):
    module = sir_command

    def setUp(self):
        super(TestSirCommandModule, self).setUp()
        self.mock_run_commands = patch(
            "ansible_collections.caribouhy.sir.plugins.modules.sir_command.run_commands",
        )
        self.run_commands = self.mock_run_commands.start()

    def tearDown(self):
        super(TestSirCommandModule, self).tearDown()
        self.mock_run_commands.stop()

    def load_fixtures(self, commands=None, filename=None):
        def load_from_file(*args, **kwargs):
            module, commands = args
            output = list()

            for item in commands:
                try:
                    command = item["command"]
                except ValueError:
                    command = item
                filename = str(command).replace(" ", "_")
                output.append(load_fixture(filename))
            return output

        self.run_commands.side_effect = load_from_file

    def test_sir_command_simple(self):
        set_module_args(dict(commands=["show system information"]))
        result = self.execute_module()
        self.assertEqual(len(result["stdout"]), 1)
        self.assertTrue(result["stdout"][0].startswith("Current-time : "))

    def test_sir_command_multiple(self):
        set_module_args(
            dict(commands=["show system information", "show system information"])
        )
        result = self.execute_module()
        self.assertEqual(len(result["stdout"]), 2)
        self.assertTrue(result["stdout"][0].startswith("Current-time : "))

    def test_sir_command_wait_for(self):
        wait_for = 'result[0] contains "System : S"'
        set_module_args(dict(commands=["show system information"], wait_for=wait_for))
        self.execute_module()

    def test_sir_command_wait_for_fails(self):
        wait_for = 'result[0] contains "test string"'
        set_module_args(dict(commands=["show system information"], wait_for=wait_for))
        self.execute_module(failed=True)
        self.assertEqual(self.run_commands.call_count, 10)

    def test_sir_command_retries(self):
        wait_for = 'result[0] contains "test string"'
        set_module_args(
            dict(commands=["show system information"], wait_for=wait_for, retries=2)
        )
        self.execute_module(failed=True)
        self.assertEqual(self.run_commands.call_count, 3)

    def test_sir_command_no_retries(self):
        wait_for = 'result[0] contains "test string"'
        set_module_args(
            dict(commands=["show system information"], wait_for=wait_for, retries=0)
        )
        self.execute_module(failed=True)
        self.assertEqual(self.run_commands.call_count, 1)

    def test_sir_command_match_any(self):
        wait_for = [
            'result[0] contains "System : S"',
            'result[0] contains "test string"',
        ]
        set_module_args(
            dict(commands=["show system information"], wait_for=wait_for, match="any")
        )
        self.execute_module()

    def test_sir_command_match_all(self):
        wait_for = [
            'result[0] contains "System : S"',
            'result[0] contains "Firm Ver. : V"',
        ]
        set_module_args(
            dict(commands=["show system information"], wait_for=wait_for, match="all")
        )
        self.execute_module()

    def test_sir_command_match_all_failure(self):
        wait_for = [
            'result[0] contains "System : S"',
            'result[0] contains "test string"',
        ]
        commands = ["show system information", "show system information"]
        set_module_args(dict(commands=commands, wait_for=wait_for, match="all"))
        self.execute_module(failed=True)

    def test_sir_command_configure_check_warning(self):
        commands = ["configure"]
        set_module_args({"commands": commands, "_ansible_check_mode": True})
        result = self.execute_module()
        self.assertEqual(
            result["warnings"],
            [
                "Only show commands are supported when using check mode, not executing configure",
            ],
        )

    def test_sir_command_configure_not_warning(self):
        commands = ["configure"]
        set_module_args(dict(commands=commands))
        result = self.execute_module()
        self.assertEqual(result["warnings"], [])
