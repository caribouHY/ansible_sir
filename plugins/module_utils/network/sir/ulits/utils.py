#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import ipaddress


def is_valid_ip(ip_str):
    try:
        ipaddress.ip_address(ip_str)
    except ValueError:
        return False
    return True
