#!/usr/bin/python
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function


__metaclass__ = type

DOCUMENTATION = """
module: sir_ping
author: caribouHY (@caribouHY)
short_description: Tests reachability using ping from Si-R router.
description:
  - Tests reachability using ping from router to a remote destination.
version_added: 1.1.0
options:
  count:
    description:
      - Number of packets to send.
    default: 5
    type: int
  afi:
    description:
      - Define echo type ip or ipv6 when dest is hostname.
    choices:
      - ip
      - ipv6
    type: str
  dest:
    description:
      - The IP Address or hostname (resolvable by router) of the remote node.
    required: true
    type: str
  df_bit:
    description:
      - Set the DF bit.
    default: false
    type: bool
  source:
    description:
      - The source IP Address.
    type: str
  size:
    description:
      - Size of the packet to send.
    type: int
  timeout:
    description:
      - Specify timeout interval.
    type: int
  state:
    description:
      - Determines if the expected result is success or fail.
    choices:
      - absent
      - present
    default: present
    type: str
  ttl:
    description:
      - The time-to-live value for the ICMP packet(s).
    type: int
notes:
  - Tested against Si-R G120 V20.54
"""

EXAMPLES = """
- name: Test reachability to 198.51.100.251
  caribouhy.sir.sir_ping:
    dest: 198.51.100.251

- name: Test un reachability to 198.51.100.253
  caribouhy.sir.sir_ping:
    dest: 198.51.100.253
    state: absent

- name: Test reachability to 198.51.100.249 using df-bit and size
  caribouhy.sir.sir_ping:
    dest: 198.51.100.249
    df_bit: true
    size: 1400

- name: Test reachability to ipv6 address
  caribouhy.sir.sir_ping:
    dest: 2001:db8:ffff:ffff:ffff:ffff:ffff:ffff
"""

RETURN = """
commands:
  description: Show the command sent.
  returned: always
  type: list
  sample: ["ping 198.51.100.251 source 192.168.10.1 repeat 20"]
packet_loss:
  description: Percentage of packets lost.
  returned: always
  type: str
  sample: "0%"
packets_rx:
  description: Packets successfully received.
  returned: always
  type: int
  sample: 20
packets_tx:
  description: Packets successfully transmitted.
  returned: always
  type: int
  sample: 20
rtt:
  description: Show RTT stats.
  returned: always
  type: dict
  sample: {"avg": 2, "max": 8, "min": 1}
"""

import re

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.caribouhy.sir.plugins.module_utils.network.sir.sir import run_commands
from ansible_collections.caribouhy.sir.plugins.module_utils.network.sir.ulits.utils import (
    is_valid_ip,
)


def generate_command(
    dest, count, afi=None, df_bit=None, source=None, size=None, timeout=None, ttl=None
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


def parse_rate(rate_info):
    rate_re = re.compile(
        r"(?P<tx>\d+) packets transmitted, (?P<rx>\d+) packets received, (?P<pkt_loss>\d+)% packet loss",
    )

    rate = rate_re.match(rate_info)
    return rate.group("pkt_loss"), rate.group("rx"), rate.group("tx")


def parse_rtt(rtt_info):
    rtt_re = re.compile(
        r"round-trip \(ms\)  min/ave/max = (?P<min>\d*).(?:\d*)/(?P<avg>\d*).(?:\d*)/(?P<max>\d+).(?:\d*)",
    )
    rtt = rtt_re.match(rtt_info)

    return rtt.groupdict()


def validate_results(module, loss, results):
    """
    This function is used to validate whether the ping results were unexpected per "state" param.
    """
    state = module.params["state"]
    if state == "present" and loss == 100:
        module.fail_json(msg="Ping failed unexpectedly", **results)
    elif state == "absent" and loss < 100:
        module.fail_json(msg="Ping succeeded unexpectedly", **results)


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    argument_spec = dict(
        count=dict(type="int", default=5),
        afi=dict(type="str", choices=["ip", "ipv6"]),
        dest=dict(type="str", required=True),
        df_bit=dict(type="bool", default=False),
        source=dict(type="str"),
        size=dict(type="int"),
        timeout=dict(type="int"),
        state=dict(type="str", choices=["absent", "present"], default="present"),
        ttl=dict(type="int"),
    )
    module = AnsibleModule(argument_spec=argument_spec)

    count = module.params["count"]
    afi = module.params["afi"]
    dest = module.params["dest"]
    df_bit = module.params["df_bit"]
    source = module.params["source"]
    size = module.params["size"]
    timeout = module.params["timeout"]
    ttl = module.params["ttl"]

    warnings = list()

    results = {}
    if warnings:
        results["warnings"] = warnings

    results["commands"] = generate_command(
        dest=dest,
        count=count,
        afi=afi,
        df_bit=df_bit,
        source=source,
        size=size,
        timeout=timeout,
        ttl=ttl,
    )
    ping_results = run_commands(module, commands=results["commands"])

    if isinstance(ping_results, list):
        ping_results = ping_results[0]

    ping_results_list = ping_results.splitlines()
    rtt_info, rate_info = None, None
    for line in ping_results_list:
        if line.startswith("round-trip"):
            rtt_info = line
        if line.startswith(f"{count} packets transmitted"):
            rate_info = line

    if rtt_info:
        rtt = parse_rtt(rtt_info)
        for k, v in rtt.items():
            if rtt[k] is not None:
                rtt[k] = int(v)
        results["rtt"] = rtt

    pkt_loss, rx, tx = parse_rate(rate_info)
    results["packet_loss"] = str(pkt_loss) + "%"
    results["packets_rx"] = int(rx)
    results["packets_tx"] = int(tx)
    validate_results(module, int(pkt_loss), results)

    module.exit_json(**results)


if __name__ == "__main__":
    main()
