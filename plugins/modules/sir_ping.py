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

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.caribouhy.sir.plugins.module_utils.network.sir.config.ping.ping import Ping


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

    result = Ping(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
