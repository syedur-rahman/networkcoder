# Quick Deploy 2.0 - Netmiko Edition

### Description

Quickly deploy commands or configuration to a selection of network devices!

### Demonstration

![](https://github.com/syedur-rahman/networkcoder/blob/master/images/netmiko_quick_deploy.gif)

### Requirements

This script was designed to be used with Python 3.

You must install the following libraries as well.

```bash
colorama==0.4.3
netmiko==2.4.2
```

### Setup & Usage

There are two files that need to be modified. The "<LINE>" are what needs to be modified.

The **devices.txt** file should contain all your devices in the following format.

```yaml
# Lines that start with # are considered comments
# Please list out every device with one line per device
# Please use a comma to add device_type or driver information for either netmiko or napalm respectively
#
# Netmiko example format, default type is cisco_ios:
# 192.168.12.109, cisco_nxos

<IP-ADDRESS/DNS>, <DEVICE-TYPE>
```

The **commands.yml** file should contain all your commands in the following format.

```yaml
# Lines that start with # are considered comments
# Please list out every command to send over to network devices
#
# If there are configuration, please use the following format:
# conf t
# interface loopback 100
# ip address 1.1.1.1 255.255.255.0
# end

conf t
<CONFIG_LINE_1>
<CONFIG_LINE_2>
end
<SHOW_COMMAND_1>
<SHOW_COMMAND_2>
```

You must wrap your configuration lines with `config t` and `end`.
