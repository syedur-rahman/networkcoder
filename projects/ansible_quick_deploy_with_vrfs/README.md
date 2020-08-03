# Ansible Quick Deploy - VRF Aware Edition

## Basic Overview

### Description

This is the [Quick Deploy Project](https://github.com/syedur-rahman/networkcoder/tree/master/projects/quick_deploy) combined with the features we created in the [Ansible VRF Routing Project](https://github.com/syedur-rahman/networkcoder/tree/master/projects/ansible_vrf_routing)!

With this, it's possible to have Ansible be fully VRF aware when running against switches. The way this is done is relatively straight forward. All you need to do is have commands with the following syntax:

```bash
show ip route vrf <vrf>
```

Our script will automatically replace the \<vrf\> with the actual vrfs that live on the switch. It will also run the non-vrf version of the command as well, which in this example would be "show ip route".

This script has been tested to be used against IOS/EOS/NXOS.



### Demonstration

![](https://github.com/syedur-rahman/networkcoder/blob/master/images/ansible_vrf_quick_deploy.gif)

### Requirements

You will need to have Ansible installed.
