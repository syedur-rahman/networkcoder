# Inventory Parse

## Basic Overview

### Description

Creates a csv of all of the output from the inventory in Cisco devices!

### Demonstration

![](https://github.com/syedur-rahman/networkcoder/blob/master/images/inventory_parse.gif)

### Requirements

This script was designed to be used with Python 3.

You must install the following libraries as well.

```bash
colorama==0.4.3
netmiko==2.4.2
```

## A Network Coder's Notes

*The below can be skipped by uninterested parties.*

# Data Transformation

Original Output:
```
NAME: "3725 chassis", DESCR: "3725 chassis"
PID: NM-16ESW=                   , VID: 0.1, SN: FTX0945W0MY

NAME: "16 Port 10BaseT/100BaseTX EtherSwitch", DESCR: "16 Port 10BaseT/100BaseTX EtherSwitch"
PID: NM-16ESW=         , VID: 1.0, SN: FTX0945W0MZ
```

Parsed Output:
```
{'name': '3725 chassis', 'descr': '3725 chassis', 'pid': '', 'vid': '0.1', 'sn': 'FTX0945W0MY'}
{'name': '16 Port 10BaseT/100BaseTX EtherSwitch', 'descr': '16 Port 10BaseT/100BaseTX EtherSwitch', 'pid': 'NM-16ESW=', 'vid': '1.0', 'sn': 'FTX0945W0MZ'}
```

Formatted for CSV:
|    Device       |	            Inventory Name              |	Description	                          | Product ID | Product Version | Serial Number |
|---------------- | --------------------------------------- | --------------------------------------- | ---------- | --------------- | ------------- |
| 192.168.160.132 |  3725 chassis                           | 3725 chassis                            |            |       0.1       | FTX0945W0MY   |
| 192.168.160.132 | 16 Port 10BaseT/100BaseTX EtherSwitch   | 16 Port 10BaseT/100BaseTX EtherSwitch   | NM-16ESW=  |       1.0       | FTX0945W0MZ   |