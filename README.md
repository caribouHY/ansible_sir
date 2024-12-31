# Ansible Collection for Si-R series

The Ansible Si-R collection includes a variety of Ansible content to help automate the management of Fasa Technologies Si-R series.

日本語版ドキュメントは[こちら](https://github.com/caribouHY/ansible_sir/blob/develop/README_jp.md)

## Version compatibility

This collection has been tested against Si-R G120 >= V20.54

### Supported connections

The Si-R collection supports ``network_cli`` connections.

## Included content
<!--start collection content-->
### Cliconf plugins
Name | Description
--- | ---
[caribouhy.sir.sir](https://github.com/caribouHY/ansible_sir/blob/main/docs/caribouhy.sir.sir_cliconf.rst)|Use sir cliconf to run command on Si-R devices.

### Modules
Name | Description
--- | ---
[caribouhy.sir.sir_command](https://github.com/caribouHY/ansible_sir/blob/main/docs/caribouhy.sir.sir_command_module.rst)|Module to run commands on Si-R devices.
[caribouhy.sir.sir_config](https://github.com/caribouHY/ansible_sir/blob/main/docs/caribouhy.sir.sir_config_module.rst)|Module to manage configuration sections.
[caribouhy.sir.sir_ping](https://github.com/caribouHY/ansible_sir/blob/main/docs/caribouhy.sir.sir_ping_module.rst)|Tests reachability using ping from Si-R router.

<!--end collection content-->

## Installing this collection

You can install the Si-R collection with the Ansible Galaxy CLI:

    ansible-galaxy collection install caribouhy.sir




## Using this collection

This collection includes [network resource modules](https://docs.ansible.com/ansible/latest/network/user_guide/network_resource_modules.html).

### Sample Playbook
```yaml
---
- name: Sample Playbook
  hosts: sir
  connection: network_cli

  tasks:
    - name: Run show system information
      caribouhy.sir.sir_command:
        commands:
          - show system information
      register: result

    - name: Debug
      ansible.builtin.debug:
        msg: "{{ result.stdout_lines[0] }}"

  vars:
    ansible_network_os: caribouhy.sir.sir
    ansible_user: admin
    ansible_ssh_pass: admin
```

<!--start requires_ansible-->
## Ansible version compatibility

This collection has been tested against following Ansible versions: **>=2.17.6**.

For collections that support Ansible 2.9, please ensure you update your `network_os` to use the
fully qualified collection name (for example, `cisco.ios.ios`).
Plugins and modules within a collection may be tested with only specific Ansible versions.
A collection may contain metadata that identifies these versions.
PEP440 is the schema used to describe the versions of Ansible.
<!--end requires_ansible-->

## Contributing to this collection

We welcome community contributions to this collection. If you find problems, please open an issue or create a PR against the [Si-R collection repository](https://github.com/caribouHY/ansible_sir). See [Contributing to Ansible-maintained collections](https://docs.ansible.com/ansible/devel/community/contributing_maintained_collections.html#contributing-maintained-collections) for complete details.

See the [Ansible Community Guide](https://docs.ansible.com/ansible/latest/community/index.html) for details on contributing to Ansible.

## Release notes

Release notes are available [here](https://github.com/caribouHY/ansible_sir/blob/master/CHANGELOG.rst).

## Licensing

GNU General Public License v3.0.

See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.

