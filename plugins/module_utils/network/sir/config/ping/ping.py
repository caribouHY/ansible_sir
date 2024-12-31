#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#

from __future__ import absolute_import, division, print_function


__metaclass__ = type

"""
The sir_ping config file.
It is in this file where the current configuration (as dict)
is compared to the provided configuration (as dict) and the command set
necessary to bring the current configuration to its desired end-state is
created.
"""

import re

from ansible_collections.caribouhy.sir.plugins.module_utils.network.sir.sir import run_commands
from ansible_collections.caribouhy.sir.plugins.module_utils.network.sir.ulits.utils import (
    is_valid_ip,
)


class Ping:
    """
    The sir_ping config class
    """

    def __init__(self, module):
        self.module = module
        self.result = {}

    def execute_module(self):
        """Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        self.generate_command()
        res = self.run_command()
        return self.process_result(res)

    def build_ping(
        self, dest, count, afi=None, df_bit=None, source=None, size=None, timeout=None, ttl=None
    ):
        """
        Genetate ping command
        """
        cmd = f"ping {dest}"

        if is_valid_ip(dest) is False and afi:
            if afi == "ip":
                cmd += " v4"
            elif afi == "ipv6":
                cmd += " v6"

        if source:
            cmd += f" source {source}"

        cmd += f" repeat {count}"

        if size:
            cmd += f" size {size}"

        if ttl:
            cmd += f" ttl {ttl}"

        if timeout:
            cmd += f" timeout {timeout}"

        if df_bit:
            cmd += " df"

        return cmd

    def validate_results(self, module, loss, results):
        """
        This function is used to validate whether the ping results were unexpected per "state" param.
        """
        state = module.params["state"]
        if state == "present" and loss == 100:
            module.fail_json(msg="Ping failed unexpectedly", **results)
        elif state == "absent" and loss < 100:
            module.fail_json(msg="Ping succeeded unexpectedly", **results)

    def generate_command(self):
        """Generate configuration commands to send based on
        want, have and desired state.
        """
        warnings = list()
        if warnings:
            self.result["warnings"] = warnings
        self.result["commands"] = self.build_ping(
            count=self.module.params["count"],
            afi=self.module.params["afi"],
            dest=self.module.params["dest"],
            df_bit=self.module.params["df_bit"],
            source=self.module.params["source"],
            size=self.module.params["size"],
            timeout=self.module.params["timeout"],
            ttl=self.module.params["ttl"],
        )

    def run_command(self):
        ping_results = run_commands(self.module, commands=self.result["commands"])
        return ping_results

    def parse_rate(self, rate_info):
        rate_re = re.compile(
            r"(?P<tx>\d+) packets transmitted, (?P<rx>\d+) packets received, (?P<pkt_loss>\d+)% packet loss",
        )

        rate = rate_re.match(rate_info)
        return rate.group("pkt_loss"), rate.group("rx"), rate.group("tx")

    def parse_rtt(self, rtt_info):
        rtt_re = re.compile(
            r"round-trip \(ms\)  min/ave/max = (?P<min>\d*).(?:\d*)/(?P<avg>\d*).(?:\d*)/(?P<max>\d+).(?:\d*)",
        )
        rtt = rtt_re.match(rtt_info)

        return rtt.groupdict()

    def process_result(self, ping_results):
        """
        Function used to parse the statistical information from the ping response.
        Returns the percent of packet loss, received packets, transmitted packets, and RTT data.
        """

        if isinstance(ping_results, list):
            ping_results = ping_results[0]

        ping_results_list = ping_results.splitlines()
        rtt_info, rate_info = None, None
        for line in ping_results_list:
            if line.startswith("round-trip"):
                rtt_info = line
            if line.startswith(f"{self.module.params['count']} packets transmitted"):
                rate_info = line

        if rtt_info:
            rtt = self.parse_rtt(rtt_info)
            for k, v in rtt.items():
                if rtt[k] is not None:
                    rtt[k] = int(v)
            self.result["rtt"] = rtt

        pkt_loss, rx, tx = self.parse_rate(rate_info)
        self.result["packet_loss"] = str(pkt_loss) + "%"
        self.result["packets_rx"] = int(rx)
        self.result["packets_tx"] = int(tx)
        self.validate_results(self.module, int(pkt_loss), self.result)
        return self.result
