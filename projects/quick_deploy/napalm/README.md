# Quick Deploy 2.0 - Napalm Edition

### Description

Quickly deploy commands or configuration to a selection of network devices!

### Demonstration

![](https://github.com/syedur-rahman/networkcoder/blob/master/images/napalm_quick_deploy.gif)

### Requirements

You must install the following libraries to use this script. The listed versions are what I used when building the Quick Deploy script. This is designed for Python 3.

```bash
colorama==0.4.3
napalm==2.5.0
```

### Setup & Usage

There are two files that need to be modified. The "<LINE>" are what needs to be modified.

The **devices.txt** file should contain all your devices in the following format.

```yaml
# Lines that start with # are considered comments
# Please list out every device with one line per device
# Please use a comma to add device_type or driver information for either netmiko or napalm respectively
#
# Napalm example format, default driver is ios:
# 192.168.12.109, nxos

<IP-ADDRESS/DNS>, <DRIVER>
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
