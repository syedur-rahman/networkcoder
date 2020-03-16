# Host Trace - Netmiko Edition

## Basic Overview

### Description

Traces a host to its interface and switch!

### Demonstration

![](https://github.com/syedur-rahman/networkcoder/blob/master/images/host_trace.gif)

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

![](https://github.com/syedur-rahman/networkcoder/blob/master/images/host_trace.png) 

### Lab: Let's Discuss Limitations
This project relies on a small number of key components. Due to this, there are quite a few limitations.

**Limitations:**

1. No Multivendor Support
2. Requires MAC/ARP Table Population
3. No Routing Support
4. No Port-channel Support

In the following sections, we will be going over the listed limitations in detail. Afterwards, we will discuss a potential solution that can address these issues.

#### No Multivendor Support
Currently, this project heavily relies on CDP. We use this protocol to determine the network topology. In other words, where to go next when tracing out a path in the network. Last but not least, the project operates under the assumption that CDP is advertising an IP Address that can be used for SSH.

This would normally not be a big deal, but a big factor with CDP is that it generally does not have multivendor support. It is almost exclusively used by Cisco products. LLDP, on the other hand, is widely supported by many vendors -- Cisco included. Depending on the kind of environment you run, it may be a good idea to swap the CDP logic out and instead use LLDP to determine the next hop of your trace.

Already, we have quite a few assumptions built into the logic of the script. Generally speaking, the less assumptions that can be made results in a more robust automation experience.

#### Requires MAC/ARP Table Population
Sometimes, devices will not show up in the ARP Table or MAC Address Table as their entries have expired. In the event that this happens, this project would not be able to gather accurate information. 

This is due to the way the logic has been set up -- we opted to take a snapshot of the current ARP and MAC Tables. The logic is not taking into account the connectivity to the host in question, nor is it trying to validate whether the device is actually online or not.

If you were to implement a similar script in production, you may want to consider adding support to remedy these issues. An easy solution would be to introduce a ping test before starting the hop trace.

#### No Routing Support
This project operates under the assumption that it can make L2 Hops till it can reach the host. When you start including L3 hops, the scope of the project becomes a lot more complex. And that's putting it lightly! 

Perhaps in a future project, we can take a look at how we can implement route tracing.

#### No Port-channel Support
Port-channels are not supported either in this project for code simplicity. This is due to the way CDP lookups work. In order to effectively trace through port-channels, we would need to reverse lookup the physical interfaces tied to the port-channels.

This is not too difficult to implement at least!

### (A) Solution
There are a number of ways to achieve a more robust and reliable script. From experience, one of the better ways is to build a dataset comprising of all the management IP Addresses tied to the switches and routers. This way, instead of relying on the address tied to the CDP (or LLDP) output, the script can rely on the dataset to determine how to best SSH to the next hop.

This kind of idea can be further extended by having a dataset for all MAC Address Tables on the network. That way, you can even eliminate the need to rely on CDP (or LLDP) altogether.

Now, the problem is figuring out how to maintain such datasets. If your environment has a tool that can be used to automatically gather data from the network (e.g. Ansible), you can use that to keep things up to date!

