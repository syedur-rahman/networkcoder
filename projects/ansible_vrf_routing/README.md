# Ansible VRF Routing

## Basic Overview

### Description

Collects the raw routing data of network devices while also being VRF-aware!

This project is more of a feature implementation. At the time of writing this article, Ansible is not vrf aware by default. This means if you use VRFs in your environment, normally you need to manually specify the names of the VRFs for Ansible to understand your intentions. This is unfortunately not a scalable solution.

Here, we will be doing a feature extension using filters. Ansible allows you to write python code via filters relatively easily. Using filters, we will have Ansible discover the VRFs automatically, then run its job based on the information it has collected.

For this demonstration, we will just have Ansible attempt to collect the routing table of each device dynamically.

### Demonstration

![](https://github.com/syedur-rahman/networkcoder/blob/master/images/ansible_vrf_routing.gif)

### Requirements

You will need to have Ansible installed.

### Usage

This script generates a log file per each device with raw data. So every device would have its own file generated, examples included in this project directory. In order to use this script, you would need to update the **devices.yml** file with your hosts.

