# NXOS Blame

## Basic Overview

### Description

Figure out who to blame for a configuration on a router or switch with an interactive interface!

This takes a spin on the previous project - [nxos_account_parse](../nxos_account_parse) - and *drastically* increases the complexity of the project.

While this is *technically* not a beginner friendly automation project, it is interesting! Hopefully this can inspire a few of you to start developing more complex automation scripts. Building a GUI can also be a very useful way to share your code with others in the team.

Oh, and yes, the project is inspired by the blame feature on GitHub.

### Demonstration

**Part 1: Startup**

![](https://github.com/syedur-rahman/networkcoderprep/blob/master/images/nxos_blame_gui.png)

This is where you can provide the details of the devices you want to analyze as well as your username and password.

**Part 2: Analysis**

![](https://github.com/syedur-rahman/networkcoderprep/blob/master/images/nxos_blame_analysis.gif)

After you type in your credentials and devices, the script goes forth and gathers all the relevant data on your behalf!

**Part 3: Blame!**

![](https://github.com/syedur-rahman/networkcoderprep/blob/master/images/nxos_blame_blame.gif)

And finally, browse through the running configuration of each device and see who did what and when.

### Requirements

This script was designed to be used with Python 3.

You must install the following libraries as well.

```bash
netmiko==2.4.2
PySide2==5.14.1
```

## A Network Coder's Notes

*The below can be skipped by uninterested parties.*

### Logic Diagram

![](https://github.com/syedur-rahman/networkcoderprep/blob/master/images/nxos_blame.png)

### Conclusion

Although the majority of us are not in the Network Engineering field to design applications, it can be quite useful to pick up a bit of GUI development skills. While the main reason is code sharing with others, there is another factor: ease of use. Sometimes a GUI is better in conveying information than CLI!

Since the project itself is sort of out of scope for beginners, we will skip the regular breakdowns/talks we usually do. However, if you have any questions, feel free to reach out.