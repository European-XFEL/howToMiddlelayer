.. role:: Python(code)
  :language: Python

Schema injection
================

A parameter injection is a modification of the class of an object. It is used
to add new parameters to an instantiated device or to update the attributes of
already existing parameters. An example for the latter is the change of the
size of an array depending on a user specified Karabo parameter.

The following code shows an example for the injection of a string and a node
into the class of a device:

.. code-block:: Python

    from karabo.middlelayer import Device

    class MyDevice(Device):

        async def onInitialization(self):
            # should it be needed to test that the node is there
            self.my_node = None

        async def inject_something(self):
            # inject a new property into our personal class:
            self.__class__.injected_string = String()
            self.__class__.my_node = Node(MyNode, displayedName="position")
            await self.publishInjectedParameters()

            # use the property as any other property:
            self.injected_string = "whatever"
            # the test that the node is there is superfluous here
            if self.my_node is not None:
                self.my_node.reached = False

    class MyNode(Configurable):
        reached = Bool(
            displayedName="On position",
            description="On position flag",
            defaultValue=True,
            accessMode=AccessMode.RECONFIGURABLE
        )

Note that calling :Python:`inject_something` again resets the values of
properties to their defaults.

Middlelayer class based injection differs strongly from C++ and
bound api parameter injection, and the following points should
be remembered:

* classes can only be injected into the top layer of the empty class
  and, consequently, of the schema rendition
* the order of injection defines the order in schema rendition
* classes injected can be simple (Double, Bool, etc.) or complex
  (Node, an entire class hierarchies, etc.)
* later modification of injected class structure is not seen in the
  schema. Modification can only be achieved by overwriting the top level
  assignment of the class and calling :func:`publishInjectedParameters`
* injected classes are not affected by later calls to
  :func:`publishInjectedParameters` used to inject other classes
* deleted (del) injected classes are removed from the schema by calling
  :func:`publishInjectedParameters`

In the above example, new properties are added to the top level class of
the device. Next, we consider the case where we want to update a property
inside a child of the top level class.


Using Overwrite to change attributes
------------------------------------

:Python:`Overwrite` is used to update the attributes of existing Karabo
property descriptors. Similar to the description in Chapter `overwrite`_  for the creation of a class,
the mechanism can be used in schema injection.

.. code-block:: Python

    class Configurator(Device):

        beckhoffComs = String(
            displayedName="BeckhoffComs in Topic",
            options=[])

        @Slot("Find BeckhoffComs")
        async def findBeckhoffComs(self):
            # Get a list of beckhoffCom deviceIds
            options = await self.get_beckhoff_coms()
            self.__class__.beckhoffComs = Overwrite(options=options)
            await self.publishInjectedParameters()

.. _schema-injection-node:

Updating attributes of properties inside a node
-----------------------------------------------

Karabo Devices are instances of a device class (classId). Hence, all instances of the same class
on the same device server share the same **static** schema and a modification to any class object
of the schema is propagated to all device children. However, as described above, it
is possible to modify the top-layer device class.
**This leads to, that a change in a noded structure requires a full reconstruction
(using a new class) and injection into the device's top level class
under the same property key.**

Below is a **MotorDevice** with two different motor axes, `rotary` and `linear` represented
in a `Node`.
In the following, we would like to change on runtime the `minInc` and `maxInc` attribute
of the `targetPosition` property. However, **Schema injection for runtime attributes in mostly
not worth it and should be avoided**. Nevertheless, this example shows the technical possiblity.

.. code-block:: Python

    from karabo.middlelayer import (
        Configurable, Device, Double, isSet, Node, String, Slot, VectorDouble)


    def get_axis_schema(key, limits=None):

        class AxisSchema(Configurable):

            node_key = key

            @Slot()
            async def updateLimits(self):
                await self.get_root().updateAxisLimits(
                    self.node_key, self.targetLimits.value)

            @VectorDouble(
                defaultValue=None,
                minSize=2, maxSize=2,
                displayedName="Target Limits")
            async def targetLimits(self, value):
                if not isSet(value):
                    self.targetLimits = value
                    return
                # Setter function always called in initialization
                self.targetLimits = value

            targetPosition = Double(
                displayedName="Value",
                minInc=limits[0] if limits is not None else None,
                maxInc=limits[1] if limits is not None else None)

        return AxisSchema


    class MotorDevice(Device):

        # Node's take classes to build up
        rotary = Node(get_axis_schema("rotary", None))
        linear = Node(get_axis_schema("linear", [0, 90]))

        async def updateAxisLimits(self, key, limits):
            # 1. Get the previous configuration from the node under `key`
            h = self.configurationAsHash()[key]
            # 2. Create a new configurable schema for `key` with `limits`
            conf_schema = get_axis_schema(key, limits)
            # 3. Set the new node on `key` and inject with previous
            # configuration `h`
            setattr(self.__class__, key, Node(conf_schema))
            await self.publishInjectedParameters(key, h)


The factory function :Python:`get_limit_schema` provides each `Node`
with a `Configurable` class.
During the creation, the `minInc` and `maxInc` attributes can be assigned to
the `targetPosition` property.
Here, the class itself has a `Slot` that propagates to the `MotorDevice`
to inject a new *Axis* under the same `key` with different limits.
During a runtime schema injection via the `Slot` *updateLimits*,
we again create a **new** updated `Configurable` class for the Node - and -
to make sure that the configuration of the `MotorDevice` is preserved, the
existing configuration is passed to the :Python:`publishInjectedParameters` method.
During the initialization, all eventual setters are called as usual.


Injecting Slots
---------------

Slots are decorating functions.
If you want to add a Slot, or change the function it is bound to (decorating),
the following will do the trick:

.. code-block:: Python

    async def very_private(self):
        self.log.INFO("This very private function is now exposed!!")

    @Slot("Inject a slot")
    async def inject_slot(self):
        # Inject a new slot in our schema
        self.__class__.injectedSlot = Slot(displayedName="Injected Slot")
        self.__class__.injectedSlot.__call__(type(self).very_private)
        await self.publishInjectedParameters()

.. note::
    The key to that slot will not be `very_private` but instead `injectedSlot`
    So yes, cool that we can change the behaviour of a slot on the fly by
    changing the function the slot calls, but the key won't reflect that.

    If you do change the functions that are called, do put in a log message.

.. warning::
    Consider instead injecting a node with a proper Slot definition.


Injected Properties and DAQ
---------------------------

Injected Properties and the DAQ need some ground rules in order to record these
properties correctly.

In order for the DAQ to record injected properties, the DAQ needs to request the
updated schema again, using the Run Controller's :func:`applyConfiguration` slot.

This can be prone to operator errors, and therefore it is recommended that only
properties injected at instantiation to be recorded.
