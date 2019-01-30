.. _device-node:

Nodes
=====

Nodes allow a device's properties to be organized in a hierarchical tree-like structure:
Devices have properties - node properties - which themselves have properties.

If a device has a node property with key `x` and the node has a property of type
double with key `y`, then the device will have a property of type double with key `x.y`.

Defining a Node's Properties
++++++++++++++++++++++++++++

To create a device with node properties, first create a class which inherits from
:class:`Configurable` with the desired properties for the node. These are
created as you would for properties of a device, at class scope, and understand
the same attribute arguments.

For example, the following class is used to create a node for a (linear) motor
axis with units in mm and actual and target position properties:

.. code-block:: Python

    class LinearAxis(Configurable):
        actualPosition = Double(
            displayedName="Actual Position",
            description="The actual position of the axis.",
            unitSymbol=Unit.METER,
            metricPrefixSymbol=MetricPrefix.MILLI,
            accessMode=AccessMode.READONLY,
            absoluteError=0.01)

        targetPosition = Double(
            displayedName="Target Position",
            description="Position argument for move.",
            unitSymbol=Unit.METER,
            metricPrefixSymbol=MetricPrefix.MILLI,
            absoluteError=0.01)

Adding Node Properties to a Device
++++++++++++++++++++++++++++++++++

Nodes are added to a device in the same way as other properties, at class
scope, using the :class:`Node` class and understand the same attribute arguments
as other properties where these make sense.

So the following creates a device with two node properties for two motor axes,
using the :class:`LinearAxis` class above:

.. code-block:: Python

    class MultiAxisController(Device):
        axis1 = Node(
            LinearAxis,
            displayedName="Axis 1",
            description="The first motor axis.")

        axis2 = Node(
            LinearAxis,
            displayedName="Axis 2",
            description="The second motor axis.")

The resulting device will have, for example, a node property with key `axis1`
and a double property with key `axis2.targetPosition`.


Node: Required Access Level
+++++++++++++++++++++++++++

To be able to access a property, a user must have access rights equal to or above
the required level for the property, specified by the `requiredAccessLevel` descriptor.
For properties belonging to nodes, the user must have the access rights for the
property and all parent nodes above it in the tree structure.

