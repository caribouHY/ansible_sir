# Ansible module for Si-R/SR-S series

Si-RG/SR-Sシリーズ用のAnsibleモジュールです。

## 使い方
`ansible_network_os: calibouhy.sir.sir`を設定してください。

## 対応機種
下記の機種でテストしています。
- Si-R G120 V20.54

## 制約事項
現状、下記モジュールによる機器操作が可能です。
- `ansible.netcommon.cli_command`
- `ansible.netcommon.cli_config`
- `ansible.netcommon.cli_backup`


ネットワーク機器に下記の設定がされている場合は正常に動作しません。
- sysnameに`+-_\/`以外の記号が含まれている場合
- terminal promptの設定がデフォルト値以外の場合