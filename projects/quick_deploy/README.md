# Quick Deploy 2.0

## Basic Overview

### Description

Quickly deploy commands or configuration to a selection of network devices!

The conceit of the **Quick Deploy 2.0** project is that the script has been designed under *three* connectivity frameworks. Remember, although there is no right or wrong way to automate tasks, some frameworks may suit your needs better. Pick whatever is right for your environment!

*The Quick Deploy 1.0 project was originally released under a different repo known as Pyability a few years back.*

### Selection

Please click a framework below to get started. The setup and requirements will be explained there.

* [Netmiko](netmiko/) - Basic SSH Framework tailored for network devices and an abstraction of **Paramiko**.
* [Napalm](napalm/) - SSH/API Framework tailored for network devices and an abstraction of **Netmiko** (and others)
* [Ansible](ansible/) - Orchestration tool designed for system and network automation.

## A Network Coder's Notes

*The below can be skipped by uninterested parties.*

### Logic Diagram

![](https://github.com/syedur-rahman/networkcoder/blob/master/images/quick_deploy.png)

For consistency, every version of the Quick Deploy script has been *roughly* designed under the same logic. 

### Features & Attributes

This section will detail relevant framework features and attributes that affect the **Quick Deploy** script.

| Features & Attributes     | netmiko | napalm | ansible |
| ------------------------- | ------- | ------ | ------- |
| nxos ssh access           | YES     | YES    | YES     |
| nxos api access           | **NO**  | YES    | YES     |
| eos ssh access            | YES     | **NO** | YES     |
| eos api access            | **NO**  | YES    | YES     |
| ios ssh access            | YES     | YES    | YES     |
| data flexibility          | YES     | YES    | **NO**  |
| configuration flexibility | YES     | **NO** | YES     |
| module flexibility        | YES     | YES    | **NO**  |

**Data Flexibility**

*Data flexibility* is the ease in which data can be manipulated within a framework. Ansible falls short here as Ansible, unlike pure Python, does not have great tools for data manipulation. The way this shortcoming was handled in **Quick Deploy 2.0** was by developing custom python filters for Ansible, which may be beyond the scope of Ansible-only engineers.

**Configuration Flexibility**

*Configuration flexibility* is a bit of a misnomer as some may argue Napalm has the *most* configuration flexibility out of all the frameworks! The only reason Napalm was listed as falling short here is due to the rigidity of the configuration update system that it enforces.

Napalm uses a unique configuration update system. Instead of enabling the user to go into `configuration terminal` directly, Napalm opts to use the device's configuration merging system instead. This means the user's configuration must be uploaded to the device's disk, then merged with the existing running configuration.

Normally, this would be a good thing. By doing it this way, Napalm opens up a few additional features. For instance, you can check what changes before and after an update. And if you find something undesirable, feel free to discard the change entirely!

Since the **Quick Deploy 2.0** script was designed to be consistent between frameworks, we are unable to take advantage of these unique features. And on top of that, being forced to upload the configuration tends to slow down the script as well.

**Module Flexibility**

*Module flexibility* is the ease at which certain features can be used within a framework. Ansible falls short here due to the nature of Ansible's ***os_config** (***os** is the vendor) modules. Due to these shortcomings, we were forced to develop with the ***os_commands** module instead.

For those unfamiliar with Ansible, the ***os_config** modules were designed specifically to handle configuration updates. As a rule of thumb, always use the more specialized modules. Not only are they more stable, they generally tend to provide greater options as well. The ***os_commands** module is a lot more generic and can be prone to failure.

Unfortunately, Ansible's ***os_config** modules does not allow us to send arbitrary configuration commands. The module classifies configuration in a hierarchy of parent and children.

See the below for an example:

```yaml
nxos_config:
  lines:
    - description test123
  parents: interface Ethernet1/12
```

While this is not normally a big deal, we are restricted by design. **Quick Deploy 2.0** is meant to be user friendly and forcing the user to classify their configuration by hierarchy would defeat the purpose. Although not ideal, for our purposes, the generic ***os_commands** module works best.

### Lab: Comparing Frameworks

Since we took the time to develop **Quick Deploy 2.0** under three separate frameworks, let's take this opportunity to perform some experiments!

Before we begin, we need to establish some rules.

#### RULES

1. Have a variety of groups in order to account for unexpected variance.

2. Have a mix of show commands and configuration commands.

3. Test the commands against each group exactly 10 times.

4. Measure and average the execution time of each attempt.

5. Unless forced to otherwise, use SSH.

   *The only exception here would be Napalm Arista, which **MUST** use API connectivity.*

Now that our rules have been established, let's go over our group and command details.

#### GROUP DETAILS

*These are the groups we will work against.*

* **Group 1 (NXOS)** - 1 Cisco Nexus Device

* **Group 2 (EOS)** - 1 Arista Device

* **Group 3 (IOS)** - 1 Cisco IOS Device

* **Group 4 (MIXED)** - 1 Cisco Nexus Device, 1 Arista Device, 1 Cisco IOS Device

* **Group 5 (MIXED)** - 2 Cisco Nexus Devices, 2 Arista Devices, 2 Cisco IOS Devices

#### COMMAND DETAILS

*These are the commands we will run against our groups*.

```bash
conf t
interface loopback100
ip address 1.1.1.1 255.255.255.0
end
show ip interface brief
conf t
interface loopback100
ip address 2.2.2.2 255.255.255.0
end
show ip interface brief
```

#### FINAL RESULTS

*The below is how long the scripts completed on average in seconds. We ran each scenario 10x.*

| FRAMEWORK | Group 1 (NXOS) | Group 2 (EOS) | Group 3 (IOS) | Group 4 (MIXED) | Group 5 (MIXED) |
| --------- | -------------- | ------------- | ------------- | --------------- | --------------- |
| netmiko   | 11.238sec      | 10.710sec     | 15.201sec     | 37.438sec       | 73.533sec       |
| napalm    | 21.578sec      | 2.388sec      | 40.858sec     | 69.649sec       | 144.148sec      |
| ansible   | 6.918sec       | 5.761sec      | 7.980sec      | 18.573sec       | 20.761sec       |

#### OBSERVATIONS

**Observation #1:** *Napalm EOS is incredibly fast!*

As we were forced to use API connectivity for Napalm EOS, we unintentionally reveal how much better API connectivity is compared to SSH. In a future project, we will explore APIs in greater depth.

**Observation #2:** *Ansible is the fastest with SSH!*

Ansible scales incredibly well. Unlike the other frameworks, Ansible, by default, is able to access multiple switches simultaneously.

But that is not all. As you noticed from this experiment, Ansible is really fast even when accessing a single device. The team that built the connectivity framework for Ansible did a great job! 

**Observation #3**: *Napalm is slower than Netmiko with SSH!*

Napalm uses Netmiko under the hood to deal with SSH. This means Napalm is partially an abstraction for Netmiko. If you understand how abstractions work, generally speaking, it's nearly impossible to find an abstraction be faster than the base!

However, this does not directly explain the *amount* of slowness of Napalm in this experiment. Napalm, unlike the other frameworks, *uploads* the configuration to the device in question first. After the upload, Napalm then goes through the merging process. These steps add additional execution time to the script.

In a project like **Quick Deploy 2.0**, Napalm tends to fall short compared to its counterparts. But that is not to say Napalm is a bad framework. Napalm has a lot to bring to the table, and we will explore this in a future project.

### Conclusion

All frameworks have their strengths and weaknesses. Some frameworks may suit a certain use case better. At the end of the day, consider any and all frameworks to be a tool to add to your automation toolbelt. And be careful not to to dismiss a tool entirely just because it did not fit your current project's needs!

With **Quick Deploy 2.0**, we discovered that our self-imposed restrictions forced us to move in certain directions. Understanding these limitations and how to get around them is key to being successful with automation.