# BGP Neighbor Advanced

## Basic Overview

### Description

Logs into specified devices and collects information about bgp neighbor peers and their interfaces and outputs it to a csv!

This is a more complete project that ties the bgp neighbor information obtained in the previous [project](https://github.com/syedur-rahman/networkcoder/blob/master/projects/bgp_neighbor_parse) to an interface obtained through the arp and mac address table.

This script will automatically log into any devices defined the devices.txt file but the device type must be a netmiko device type.

### Demonstration

![](https://github.com/syedur-rahman/networkcoder/blob/master/images/bgp_neighbor_adv.gif)

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

This script collects bgp neighbor information from the command ```show ip bgp neighbor``` and checks the arp table and mac address table for the bgp neighbor IP address to retrieve the interface.

This project also heavily relies on code from a previous project named [mac arp parse](https://github.com/syedur-rahman/networkcoder/blob/master/projects/mac_arp_parse)

# Example Output
| Device            | BGP Neighbor IP | Interface       | Router ID	 | State       | Prefixes Received | Neighbor AS | Uptime   |Description             |
| ----------------- | --------------- | --------------- | ---------- | ----------- | ----------------- | ----------- | -------- | ---------------------- |
| 192.168.160.132   | 172.31.6.1	  | FastEthernet1/2	| 10.1.0.1	 | Established | 3                 | 65501	     | 8:21:31  | N/A                    |
| 192.168.160.132	| 172.31.6.3	  | FastEthernet1/1	| 172.31.6.3 | Established | 3                 | 65502	     | 8:21:31  | N/A                    |
| 192.168.160.133	| 172.31.6.2	  | FastEthernet1/2	| 10.2.0.1	 | Established | 4                 | 65500	     | 8:21:42  | Router 2 in Las Vegas  |
| 192.168.160.134	| 172.31.6.2	  | FastEthernet1/1	| 10.2.0.1	 | Established | 5                 | 65500	     | 8:21:53  | N/A                    |


# Disclaimer

This script has been tested successfully in an IOS only environment.

For other systems, modifications may be needed.