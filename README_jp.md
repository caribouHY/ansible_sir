# Ansible module for Si-R series

Si-Rシリーズ用のAnsibleモジュールです。

## モジュール一覧

モジュール名 | 説明
--- | ---
[caribouhy.sir.sir_command](https://github.com/caribouHY/ansible_sir/blob/main/docs/caribouhy.sir.sir_command_module.rst)|Si-R上で運用管理コマンドを実行します。

## Sample Playbook
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

## 対応機種
下記の機種でテストしています。
- Si-R G120 V20.54

## 制約事項
Si-Rに下記の設定がされている場合は正常に動作しません。
- sysnameに`+-_\/`以外の記号が含まれている場合
- terminal promptの設定がデフォルト値以外の場合

## Licence
### GPL V3
See the [LICENSE](LICENSE) file.