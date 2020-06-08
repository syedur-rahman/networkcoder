# Map Network Advanced - Napalm Edition

## Basic Overview

### Description

Create an advanced network diagram automatically with Napalm!!

This is a follow-up to the previous project where we created a very basic and generic graph using networkx and matplotlib.

Here, we opt out of using matplotlib and instead use graphviz. Graphviz is a powerful graphing utility that enables us to have a lot more control over how our graphs are generated. We can even graph multiple connections without them overlapping! This is a surprisingly difficult problem to resolve.

This project is based on lldp neighbors.

### Demonstration

![](https://github.com/syedur-rahman/networkcoder/blob/master/images/map_network_adv.gif)

### Requirements

This script was designed to be used with Python 3.

You must install the following libraries as well.

```bash
colorama==0.4.3
napalm==2.5.0
networkx==2.4
pygraphviz==1.5
```

The last library on the list can be a bit difficult to install. You will need to have the application, graphviz, installed on your system first and you may need to resolve a few other dependencies.

### Usage

The script does not directly generate a graph file and instead just generates a dot file. A dot file has parameters that can be used by graphviz to generate a graph of your liking. I recommend running the basic command as suggested below, but feel free to adjust to fit your needs. There are quite a few different types of layout algorithms that can be used.

**Suggested command:**

```bash
dot -T png graph.dot > advanced_graph.png
```

### Limitations

Although we are calling this an "advanced" map script, in reality there are still a few limitations that can be overcome with a more thorough design. The main one is that this script does not generate a dynamic javascript map, which can be incredibly useful for larger scale diagrams.

### Example Output

![](https://github.com/syedur-rahman/networkcoder/blob/master/images/advanced_graph.png)