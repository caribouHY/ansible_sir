#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#

from __future__ import absolute_import, division, print_function


__metaclass__ = type
from textwrap import dedent
from unittest.mock import patch

from ansible_collections.caribouhy.sir.plugins.modules import sir_ping
from ansible_collections.caribouhy.sir.tests.unit.modules.utils import set_module_args

from .sir_module import TestSirModule


class TestSirPingModule(TestSirModule):
    module = sir_ping

    def setUp(self):
        super(TestSirPingModule, self).setUp()
        self.mock_execute_show_command = patch(
            "ansible_collections.caribouhy.sir.plugins.modules.sir_ping.run_commands",
        )
        self.execute_show_command = self.mock_execute_show_command.start()

    def tearDown(self):
        super(TestSirPingModule, self).tearDown()
        self.mock_execute_show_command.stop()

    def test_sir_ping_count(self):
        self.execute_show_command.return_value = dedent(
            """\
            PING 8.8.8.8: 46 data bytes.
            54 bytes from 8.8.8.8: icmp_seq=0 ttl=60 time=5.549 ms
            54 bytes from 8.8.8.8: icmp_seq=1 ttl=60 time=4.814 ms

            ----8.8.8.8 PING Statistics----
            2 packets transmitted, 2 packets received, 0% packet loss
            round-trip (ms)  min/ave/max = 4.814/5.181/5.549
            """,
        )
        set_module_args(dict(count=2, dest="8.8.8.8"))
        result = self.execute_module()
        mock_res = {
            "commands": "ping 8.8.8.8 repeat 2",
            "packet_loss": "0%",
            "packets_rx": 2,
            "packets_tx": 2,
            "rtt": {"min": 4, "avg": 5, "max": 5},
            "changed": False,
        }
        self.assertEqual(result, mock_res)

    def test_sir_ping_v6(self):
        self.execute_show_command.return_value = dedent(
            """\
            PING (94=40+8+46 bytes) 2001:db8:ffff:ffff:ffff:ffff:ffff:ffff --> 2404:6800:4004:818::2004
            54 bytes from 2404:6800:4004:818::2004 icmp_seq=0 hlim=57 time=6.857 ms
            54 bytes from 2404:6800:4004:818::2004 icmp_seq=1 hlim=57 time=4.795 ms

            ----2404:6800:4004:818::2004 PING Statistics----
            2 packets transmitted, 2 packets received, 0% packet loss
            round-trip (ms)  min/ave/max = 4.795/5.826/6.857
            """,
        )
        set_module_args(
            dict(count=2, dest="www.google.com", afi="ipv6"),
        )
        result = self.execute_module()
        mock_res = {
            "commands": "ping www.google.com v6 repeat 2",
            "packet_loss": "0%",
            "packets_rx": 2,
            "packets_tx": 2,
            "rtt": {"min": 4, "avg": 5, "max": 6},
            "changed": False,
        }
        self.assertEqual(result, mock_res)

    def test_sir_ping_options_all(self):
        self.execute_show_command.return_value = dedent(
            """\
            PING 142.250.196.132: 800 data bytes.
            808 bytes from 142.250.196.132: icmp_seq=0 ttl=60 time=5.302 ms
            808 bytes from 142.250.196.132: icmp_seq=1 ttl=60 time=4.790 ms
            808 bytes from 142.250.196.132: icmp_seq=2 ttl=60 time=5.872 ms
            808 bytes from 142.250.196.132: icmp_seq=3 ttl=60 time=5.490 ms

            ----142.250.196.132 PING Statistics----
            4 packets transmitted, 4 packets received, 0% packet loss
            round-trip (ms)  min/ave/max = 4.790/5.363/5.872
            """,
        )
        set_module_args(
            {
                "afi": "ip",
                "count": 4,
                "dest": "www.google.com",
                "size": 800,
                "df_bit": True,
                "source": "10.1.1.1",
                "timeout": 5,
                "state": "present",
                "ttl": 100,
            },
        )
        result = self.execute_module()
        mock_res = {
            "commands": "ping www.google.com v4 source 10.1.1.1 repeat 4 size 800 ttl 100 timeout 5 df",
            "packet_loss": "0%",
            "packets_rx": 4,
            "packets_tx": 4,
            "rtt": {"min": 4, "avg": 5, "max": 5},
            "changed": False,
        }
        self.assertEqual(result, mock_res)

    def test_sir_ping_fail(self):
        self.execute_show_command.return_value = dedent(
            """\
            PING 10.1.1.250: 46 data bytes.

            ----10.1.1.250 PING Statistics----
            2 packets transmitted, 0 packets received, 100% packet loss
            """,
        )
        set_module_args(dict(count=2, dest="10.1.1.250", state="present"))
        result = self.execute_module(failed=True)
        mock_res = {
            "msg": "Ping failed unexpectedly",
            "commands": "ping 10.1.1.250 repeat 2",
            "packet_loss": "100%",
            "packets_rx": 0,
            "packets_tx": 2,
            "failed": True,
        }
        self.assertEqual(result, mock_res)

    def test_sir_ping_state_absent_pass(self):
        self.execute_show_command.return_value = dedent(
            """\
            PING 10.1.1.250: 46 data bytes.

            ----10.1.1.250 PING Statistics----
            2 packets transmitted, 0 packets received, 100% packet loss
            """,
        )
        set_module_args(dict(count=2, dest="10.1.1.250", state="absent"))
        result = self.execute_module()
        mock_res = {
            "commands": "ping 10.1.1.250 repeat 2",
            "packet_loss": "100%",
            "packets_rx": 0,
            "packets_tx": 2,
            "changed": False,
        }
        self.assertEqual(result, mock_res)

    def test_sir_ping_state_absent_fail(self):
        self.execute_show_command.return_value = dedent(
            """\
            PING 8.8.8.8: 46 data bytes.
            54 bytes from 8.8.8.8: icmp_seq=0 ttl=60 time=5.549 ms

            ----8.8.8.8 PING Statistics----
            2 packets transmitted, 1 packets received, 50% packet loss
            round-trip (ms)  min/ave/max = 5.549/5.549/5.549
            """,
        )
        set_module_args(dict(count=2, dest="8.8.8.8", state="absent"))
        result = self.execute_module(failed=True)
        mock_res = {
            "msg": "Ping succeeded unexpectedly",
            "commands": "ping 8.8.8.8 repeat 2",
            "packet_loss": "50%",
            "packets_rx": 1,
            "packets_tx": 2,
            "rtt": {"min": 5, "avg": 5, "max": 5},
            "failed": True,
        }
        self.assertEqual(result, mock_res)
