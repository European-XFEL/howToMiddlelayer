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

Updating properties inside a node
---------------------------------

Suppose in a device there are multiple nodes that are set up from the
same base class. In this case, there are multiple instances of the same class,
one in each node, and a modification of this class will modify all nodes.
Also, a modification of any class except for the device's top level class
will modify the respective instances in ANY of the device instances running on
the server. Only a device's top level class is protected. A change in a child
class requires a full reconstruction of the child in a fresh class and an
injection into the device's top level class.

As an example on how a schema injection can be used to update the attributes
of a property inside a node, we update the :Python:`description` attribute
of a Karabo value :Python:`importantValue` based on the value of a Karabo
string :Python:`description`. The updated node is injected into the device's
top level class.

Example
+++++++

The factory function :Python:`create_test_channel` is used to create nodes of the same 'type', which, however,
incorporate different classes. Here, same 'type' means that all nodes of this 'type' have the same
layout of Karabo properties, e.g. if there are multiple input channels present
in a device.

.. code-block:: Python

    from karabo.middlelayer import (
        Configurable, Device, Double, isSet, Node, String
    )

    from ._version import version as deviceVersion


    def create_test_channel(conf=None):
        class TestChannel(Configurable):

            async def update_important_value_description(self):
                dev = next(iter(self._parents))
                key = self._parents[dev]

                await dev.update_test_channel_important_value_descrpt(key)

            @String(
                displayedName="description",
                description="Update description of the Important Value"
            )
            async def description(self, val):
                if not isSet(val) or val.value is None:
                    return
                self.description = val.value

                if self.get_root().allow_update:
                    await self.update_important_value_description()

            if conf:
                importantValue = Double(
                    displayedName="Important Value",
                    description=conf["description"]
                )
            else:
                importantValue = Double(
                    displayedName="Important Value",
                    description="Important Value"
                )

        return TestChannel


    class SchemaInjectionExample1(Device):
        __version__ = deviceVersion

        def __init__(self, configuration):
            super().__init__(configuration)

        testChannel1 = Node(create_test_channel())
        testChannel2 = Node(create_test_channel())
        allow_update = False

        async def update_test_channel_important_value_descrpt(self, node_key):
            self.allow_update = False
            h = self.configurationAsHash()[node_key]
            setattr(self.__class__, node_key, Node(create_test_channel(h)))

            await self.publishInjectedParameters(node_key, h)
            self.allow_update = True

        async def onInitialization(self):
            """ This method will be called when the device starts.

                Define your actions to be executed after instantiation.
            """
            self.allow_update = True



The factory function :Python:`create_test_channel` ensures that each of the
nodes has a different class, so that a class update by a schema injection only
affects a single node. The attribute of a specific property inside a node can
be assigned during class contruction. In the example, the previous
configuration of the node is stored as a Karabo Hash and given to the class
factory as an argument. From the configuration Hash, the new description
for the :Python:`importantValue` is extracted. During the schema injection
the new node instance is initialized with the values of the old node instance
by passing the configuration Hash of the old node to the
:Python:`publishInjectedParameters` function. Note that during the
initialization the setter functions of the properties are called. To prevent
an infinite schema injection cascade, the bool :Python:`allow_update` is used.

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
