# Inventory Parse

## Basic Overview

### Description

Generates csv outputs to create a profile of a device!

This is a followup to the previous project which created parsing logic for just getting the actual hardware inventory components.

This project leverages napalm to get even more information of the device including parameters such as uptime, OS version, serial number and more to create a more complete device profile.

### Demonstration

![](https://github.com/syedur-rahman/networkcoder/blob/master/images/device_profiler.gif)

### Requirements

This script was designed to be used with Python 3.

You must install the following libraries as well.

```bash
colorama==0.4.3
napalm==2.5.0
```

## A Network Coder's Notes

*The below can be skipped by uninterested parties.*

# Usage

This script generates two csv log files: one with all hardware inventory components and another one that gets statistical information and the status of hardware and software components.

A couple parameters are output as raw dictionaries when needed (i.e. multiple cpu cores, multiple switch stacks, etc)

# Disclaimer

This script has been tested successfully in an IOS only environment.

For other systems, modifications may be needed.