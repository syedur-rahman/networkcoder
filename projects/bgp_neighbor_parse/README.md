# Inventory Parse

## Basic Overview

### Description

Logs into specified devices and collects information about bgp neighbor peers and outputs it to the command line!

This script will automatically log into any devices defined the devices.txt file but the device type must be a netmiko device type.

### Demonstration

![](https://github.com/syedur-rahman/networkcoder/blob/master/images/bgp_neighbor_parse.gif)

### Requirements

This script was designed to be used with Python 3.

You must install the following libraries as well.

```bash
colorama==0.4.3
netmiko==2.4.2
```

## A Network Coder's Notes

*The below can be skipped by uninterested parties.*

# Usage

This script collects bgp neighbor information from the command ```show ip bgp neighbor``` and outputs it to the command line into a parsed format.

# Disclaimer

This script has been tested successfully in an IOS only environment.

For other systems, modifications may be needed.