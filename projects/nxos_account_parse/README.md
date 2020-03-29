# NXOS Account Parse

## Basic Overview

### Description

Generate a spreadsheet of all changes on a Cisco Nexus device!

Cisco Nexus has a very useful command known as *"show accounting log all"*. This command keeps track of changes performed on the device. This includes what the changes were, as well as who did the changes.

The output, unfortunately, is...not ideal, to put it lightly. That is where automation comes into play! We'll take the messy output and *transform* it into something a lot more useful.

The idea of this project is to showcase an example where automation is used to *transform* data into something a lot more meaningful.

### Demonstration

![](https://github.com/syedur-rahman/networkcoder/blob/master/images/nxos_account_parse.gif)

### Requirements

This script was designed to be used with Python 3.

You must install the following libraries as well.

```bash
colorama==0.4.3
netmiko==2.4.2
```

### Original Output

```
Thu Jan 30 01:41:15 2020:type=update:id=192.168.12.138@pts/3:user=frank:cmd=configure terminal ; feature scp-server (SUCCESS)
Mon Feb 10 09:30:45 2020:type=update:id=192.168.12.138@pts/3:user=ethan:cmd=configure terminal ; interface Ethernet1/10 ; description "this is a new interface" (SUCCESS)
```

### Transformed Output

| DATE       | USER  | CHANGE                                                       |
| ---------- | ----- | ------------------------------------------------------------ |
| 2020-02-10 | ethan | interface Ethernet1/10<br />description "this is a new interface" |
| 2020-01-30 | frank | feature scp-server                                           |

## A Network Coder's Notes

*The below can be skipped by uninterested parties.*

### Logic Diagram

![](https://github.com/syedur-rahman/networkcoder/blob/master/images/nxos_account_parse.png) 

### Parse Logic

![](https://github.com/syedur-rahman/networkcoder/blob/master/images/parse_accounting_log.png) 

This type of parsing is a little bit more complex than regular parsing simply because we need to be able to transform the date into something a little more user friendly.

The way this is done here is via using a python library - `datetime`. This enables us to transform the Cisco date format into a date object, which we can later manipulate into whatever date format we prefer.

One strange aspect of the parse logic that you might have noticed is that we are *only* grabbing the last line of the configuration. This is used to avoid duplicates in our dataset. As you can see below, the output of the accounting log command has every line of the configuration as a separate entry.

```
Mon Feb 10 09:30:45 2020:type=update:id=192.168.12.138@pts/3:user=ethan:cmd=configure terminal ; interface Ethernet1/10 (SUCCESS)
Mon Feb 10 09:30:45 2020:type=update:id=192.168.12.138@pts/3:user=ethan:cmd=configure terminal ; interface Ethernet1/10 ; description "this is a new interface" (SUCCESS)
```

Since the output contains redundant information, we should be fine with grabbing just the latest information from each line. This will remove the need to include duplication removal logic in our code.

### Conclusion

Parsing is the current unfortunate reality of automation as a Network Engineer. At the time of writing, the *'show accounting log all'* does not have a structured equivalent, so no matter how you decide to grab this data, it will need to be parsed to be of any use. Once you get used to parsing, automation should become a lot easier.

In future projects, we'll explore other kinds of parsing systems, such as **TextFSM**.