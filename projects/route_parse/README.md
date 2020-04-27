# Route Parse

## Basic Overview

### Description

Parses the routing table on a network device and formats it into an easy to read csv file!

### Demonstration

![](https://github.com/syedur-rahman/networkcoder/blob/master/images/route_parse.gif)

### Requirements

This script was designed to be used with Python 3.

You must install the following libraries as well.

```bash
colorama==0.4.3
netmiko==2.4.2
```
### Original Output

```
C       172.31.6.0 is directly connected, Vlan6
     10.0.0.0/8 is variably subnetted, 4 subnets, 2 masks
B       10.2.0.0/24 [20/0] via 172.31.6.2, 02:28:38
D       10.3.0.0/24 [90/156160] via 172.31.6.3, 02:28:52, Vlan6
                    [90/156160] via 172.31.3.1, 02:28:53, Vlan3
O       10.2.0.1/32 [110/2] via 172.31.6.2, 02:28:45, Vlan6
                    [110/2] via 172.31.3.2, 02:28:45, Vlan3
     172.31.0.0/24 is subnetted, 4 subnets
C       172.31.3.0 is directly connected, Vlan3
S       172.31.2.0 is directly connected, FastEthernet0/0

```

### Transformed Output

|   Network    | Destination    | Routing Protocol |
|------------- | -------------  | ---------------- |
|172.31.6.0/24 | Vlan6          | Connected        |
|10.2.0.0/24   | 172.31.6.2     | BGP              |
|10.3.0.0/24   | 172.31.6.3     | EIGRP            |
|10.3.0.0/24   | 172.31.3.1     | EIGRP            |
|10.2.0.1/32   | 172.31.6.2     | OSPF             |
|10.2.0.1/32   | 172.31.3.2     | OSPF             |
|172.31.3.0/24 | Vlan3          | Connected        |
|172.31.2.0/24 | FastEthernet0/0| Static           |

## A Network Coder's Notes

*The below can be skipped by uninterested parties.*

### Logic Diagram

![](https://github.com/syedur-rahman/networkcoder/blob/master/images/route_parse.png)

### Parse Logic
![](https://github.com/syedur-rahman/networkcoder/blob/master/images/route_parse_log.png)

This parsing is made more complicated than it normally should due to how cisco formats the routing table in IOS and IOS-XE.

It is rather simple when there is just one host advertising the route, like below:
 ```
 C       172.31.6.0 is directly connected, Vlan6
 ```

However, it becomes more complicated when multiple routes with the same cost are being advertised.

One example of this is the below:
```
O       10.2.0.1/32 [110/2] via 172.31.6.2, 02:28:45, Vlan6
                    [110/2] via 172.31.3.2, 02:28:45, Vlan3
```

In this instance, the network is omitted on subsequent lines so there has to be parsing logic in place to store the network and mask since it doesn't show up on the second line.
There are other instances besides this where the mask is omitted if the CIDR is the same for each route and they're part of the same classful network.

### Conclusion
Unfortunately, not all CLI outputs are formatted in an easy way to parse since the original design doesn't account for automation.

The sooner APIs take over, the better!


