# Trace Route

## Basic Overview

### Description

Traces a network to its native location easily!

### Demonstration

![](https://github.com/syedur-rahman/networkcoder/blob/master/images/trace_route.gif)

### Requirements

This script was designed to be used with Python 3.

You must install the following libraries as well.

```bash
colorama==0.4.3
netmiko==2.4.2
```

## A Network Coder's Notes

*The below can be skipped by uninterested parties.*

### Logic Diagram

![](https://github.com/syedur-rahman/networkcoder/blob/master/images/trace_route.png)

## Disclaimer
This script has been tested successfully in an IOS only environment.

In addition, it requires CDP to function and needs the cdp advertised IP address to be reachable.

For other systems, modifications may be needed.

## Reliance
This script heavily relies on a previous project, [Host Trace](https://github.com/syedur-rahman/networkcoder/blob/master/projects/host_trace) in order to get the actual next hop interface when the next hop interface is a Vlan or Loopback address.

Let's say as an example **10.3.0.0/24** was being traced (relevant excerpts of routing table below)

```
D       10.3.0.0/24 [90/156160] via 172.31.6.3, 07:07:43, Vlan6
C       172.31.6.0 is directly connected, Vlan6
```

In this type of instance, there are two options available: either ssh to 172.31.6.3 and hope it's reachable or check the ARP table for the mac address and then the CAM table for the interface so that the cdp advertised IP can be tried instead.

I opted for the second method because the CDP advertised IP address is more often going to be reachable as opposed to a peering IP address.

I've included the relevant components of the ARP and CAM table below

**ARP Table**
```
Protocol  Address          Age (min)  Hardware Addr   Type   Interface
Internet  172.31.6.3             65   c203.0726.0000  ARPA   Vlan6
```

**CAM Table**
```
Destination Address  Address Type  VLAN  Destination Port
-------------------  ------------  ----  --------------------
c203.0726.0000          Dynamic       6     FastEthernet1/1
```

From here, the CDP table can be checked for FastEthernet1/1 and an IP address can be obtained to which the script can ssh to to continue the network trace.

## Conclusion
While this is only a POC (proof of concept), it was very involved in order to have things function properly.

This project is a good display of how even though a different script may be created for an entirely different reason, it is possible to leverage that code to accomplish other tasks as well.



