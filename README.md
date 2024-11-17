# Ansible Collection for Si-R series

The Ansible Cisco IOS collection includes a variety of Ansible content to help automate the management of Fasa Technologies Si-R series.

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

<!--end collection content-->

## Installing this collection

You can install the Si-R collection with the Ansible Galaxy CLI:

    ansible-galaxy collection install caribouhy.sir




## Using this collection

This collection includes [network resource modules](https://docs.ansible.com/ansible/latest/network/user_guide/network_resource_modules.html).

### Using modules from the Allied Telesis AlliedWare Plus collection in your playbooks

You can call modules by their Fully Qualified Collection Namespace (FQCN), such as `alliedtelesis.awplus.awplus_l2_interfaces`.

The following task replaces configuration changes in the running configuration on an Allied Telesis AW+ network device, using the FQCN:

```yaml
---
  - name: Replace device configuration of specified L2 interfaces with provided configuration.
    alliedtelesis.awplus.awplus_l2_interfaces:
      config:
        - name: port1.0.1
          trunk:
            allowed_vlans: 20-25,40
            native_vlan: 20
      state: replaced
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

We welcome community contributions to this collection. If you find problems, please open an issue or create a PR against the [Allied Telesis AlliedWare Plus collection repository](https://github.com/alliedtelesis/ansible_awplus). See [Contributing to Ansible-maintained collections](https://docs.ansible.com/ansible/devel/community/contributing_maintained_collections.html#contributing-maintained-collections) for complete details.

See the [Ansible Community Guide](https://docs.ansible.com/ansible/latest/community/index.html) for details on contributing to Ansible.

## Release notes

Release notes are available [here](https://github.com/alliedtelesis/ansible_awplus/blob/master/CHANGELOG.rst).

## Licensing

GNU General Public License v3.0.

See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.

