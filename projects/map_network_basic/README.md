# Map Network Basic - Napalm Edition

## Basic Overview

### Description

Create a very basic network diagram automatically with Napalm!!

Combined with a few graphing libraries, we can use napalm to very quickly generate a map of the network in as little lines of code as possible. This is one of the greatest advantages of using napalm - giving you consistent structured data sets.

This is specifically based on lldp neighbors.

### Demonstration

![](https://github.com/syedur-rahman/networkcoder/blob/master/images/map_network_basic.gif)

### Requirements

This script was designed to be used with Python 3.

You must install the following libraries as well.

```bash
colorama==0.4.3
napalm==2.5.0
networkx==2.4
matplotlib==3.2.1
```

### Limitations

This is labeled as a "basic" script for a reason - there are a ton of limitations!

The biggest one is that this script does not function well at scale and with multiple connections between the same node. And it is not a dynamic graph, leaving scaling and resizing a chore to deal with.

In a future script, we will overcome these limitations and explore a lot more graphing possibilities. Stay tuned!

### Example Output

![](https://github.com/syedur-rahman/networkcoder/blob/master/images/basic_diagram.png)