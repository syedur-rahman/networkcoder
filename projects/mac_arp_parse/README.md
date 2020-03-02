# MAC ARP Parse - Netmiko Edition

## Basic Overview

### Description

Collect and combines the MAC and ARP tables from network devices!

### Demonstration

![](https://github.com/syedur-rahman/networkcoder/blob/master/images/mac_arp_parse.gif)

### CSV Output Format
| Device        | MAC Address    | IP Address  | Interface          |
| ------------- | ------------   | ----------- | -----------------  |
| 192.168.10.30 | 0050.7966.6800 | 172.31.3.21 | FastEthernet1/0    |
| test_host1    | 0050.7966.6805 | 10.68.25.32 | Vlan4              |
| 192.168.30.20 | 0050.7966.6803 | 10.67.21.23 | GigabitEthernet1/0 |

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

![](https://github.com/syedur-rahman/networkcoder/blob/master/images/mac_arp_parse.png) 

### Parsing Logic
There are three main sections that comprises this script:

1. Parse: MAC Address Table
2. Parse: ARP Table
3. Compare: ARP and MAC Tables

#### Parse: MAC Address Table

The typical format of a **MAC Address Table** on Cisco devices roughly looks like the below:

| Destination Address   | Address Type | VLAN  | Destination Port     |
| --------------------- | ------------ |  ---- | -------------------- |
| c201.04d3.0000        |  Self        | 1     | Vlan1                |
| c201.04d3.0000        |  Self        | 4     | Vlan4                |
| 0050.7966.6800        |  Dynamic     | 4     | FastEthernet1/0      |
| 0050.7966.6805        |  Dynamic     | 4     | FastEthernet1/0      |

There are two ways to parse this output - **strict** vs **flexible**.

**Strict Parsing**

![](https://github.com/syedur-rahman/networkcoder/blob/master/images/parse_mac_address_table_strict.png)

Operating in a strict manner just means making additional assumptions. And assumptions can be deadly!

For instance, we could have *assumed* the first column will *always* contain the mac address. If you have worked long enough with network devices, you will know that the format of show commands is never consistent! It depends heavily on the model of the device as well as the code. By making assumptions, you end up introducing additional risk of failure.

The key to success when it comes to parsing raw data is to make as few assumptions as possible.

**Flexible Parsing**

![](https://github.com/syedur-rahman/networkcoder/blob/master/images/parse_mac_address_table_flexible.png)

What we instead opted for was a more flexible approach that *searches* for the structure of a mac address and interface, as opposed to the assumption of where it is supposed to appear.

This was achieved by the following code:
```python
for line in raw_mac_table.splitlines():
    # define variables so that dictionary doesn't error out
    interface = ''
    mac_address = ''
        
    # split based on white space
    line_parameters = line.split()
        
    # iterate over parameters and check for mac address and interface
    for parameter in line_parameters:
        
        # check for mac address
        if parameter.count('.') == 2:
            mac_address = parameter
            
        # check for interface
        if '/' in parameter.lower() or 'vlan' in parameter.lower():
            interface = parameter
                
    # store information into a dictionary for easy access
    if interface and mac_address:
        mac_parse_dict[mac_address] = {'interface': interface}
```

In this code, a mac address or interface is determined via the following logic:

1. If the format is a typical cisco mac address format, then assume mac address (i.e. c201.04d3.0000)
2. If the parameter has a "/" or "vlan", then assume interface.

This logic can easily be extended to include Port-channels, Tunnels, etc. if required.

#### Parse: ARP Table

The typical format of the **ARP Table** on Cisco devices roughly looks like the below:

| Protocol |  Address        | Age (min) | Hardware Addr  | Type | Interface        |
| -------- | --------------- | --------- | -------------- | ---- | ---------------- |
| Internet | 192.168.160.129 | -         | c201.04d3.0000 | ARPA |  FastEthernet0/0 |
| Internet | 172.31.0.21     | 169       | 0050.7966.6800 | ARPA |  Vlan4           |
| Internet | 172.31.0.20     | 169       | 0050.7966.6805 | ARPA |  Vlan4           |
| Internet | 172.31.0.1      | -         | c201.04d3.0000 | ARPA |  Vlan4           |

Similar to the **MAC Address Table**, we could do a location based approach and assume the second column is the IP address and the last column is the interface. However, as stated previously, the problem with this approach is that it relies on the assumption of consistency.

We can instead opt for a more dynamic approach that checks for the format of an IP Address or MAC Address. This allows our code to be both more simplistic and robust.

This was achieved by the following code:
```       python
for line in raw_arp_table.splitlines():
    ip_address = ''
    mac_address = ''
    
    # split based on white space
    line_parameters = line.split()
            
    # iterate over parameters and check for mac address and ip address
    for parameter in line_parameters:
        # check for mac address
        if parameter.count('.') == 2:
            mac_address = parameter
                    
        # check for ip address
        if parameter.count('.') == 3:
            ip_address = parameter
            
    # store information into a dictionary for easy access
    if mac_address and ip_address:
        arp_parse_dict[mac_address] = {'ip_address': ip_address}
```


#### Compare: ARP and MAC Tables

The final portion of our logic is to map the mac address in the **ARP Table** to the mac address in the **MAC Address Table** to provide an end-to-end holistic view.

In addition, any entries that are *only* in the arp table that aren't in the mac address table are filtered out. Non-host mac address entries were not accounted for as well.

The end goal of this script is to be able to tie the interfaces together with the IP Address, so including arp entries that aren't in the mac table would defeat the purpose.

So how is this comparison done? By the following code:
```     python
for mac_address, mac_parse_values in parsed_arp_table.items():
            
    # check if mac address from arp table is in mac address table
    if mac_address in parsed_mac_table:
    
    	interface = parsed_mac_table[mac_address]['interface']
    	ip_address = arp_parse_values['ip_address']
                
    	# write information to csv log file
    	mac_arp_csv_writer.writerow([device, mac_address, ip_address, interface])
```
As both `parsed_arp_table` and `parsed_mac_table` were designed to have the MAC address as the keys, comparing is relatively straightforward. All we need to do is loop over the `parsed_arp_table` and check if the mac address exists within the `parsed_mac_table` dictionary. Then we can combine the data within both dictionaries and output the result as a CSV.

