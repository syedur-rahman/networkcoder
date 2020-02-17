# Quick Deploy 2.0 - Ansible Edition

### Description

Quickly deploy commands or configuration to a selection of network devices!

### Demonstration

![](https://github.com/syedur-rahman/networkcoder/blob/master/images/ansible_quick_deploy.gif)

### Requirements

You only need Ansible with Python 3 installed.

### Setup & Usage

There are two files that need to be modified. The "<LINE>" are what needs to be modified.

The **devices.yml** file should contain all your devices in the following format.

```yaml
all:
  hosts:
  children:
    nxos:
      hosts:
        <NEXUS-HOSTNAME-2>:
          ansible_host: <IP-ADDRESS/DNS>
        <NEXUS-HOSTNAME-2>:
          ansible_host: <IP-ADDRESS/DNS>
    eos:
      hosts:
        <ARISTA-HOSTNAME-1>:
          ansible_host: <IP-ADDRESS/DNS>
    ios:
      hosts:
        <IOS-HOSTNAME-1>:
          ansible_host: <IP-ADDRESS/DNS>
```

The **commands.yml** file should contain all your commands in the following format.

```yaml
device_commands:
  - 'config t'
  - <CONFIGURATION_LINE_1>
  - <CONFIGURATION_LINE_2>
  - 'end'
  - <SHOW_COMMAND_1>
  - <SHOW_COMMAND_2>
```

You must wrap your configuration lines with `config t` and `end`.

