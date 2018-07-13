Schema injection
================


A parameter injection is a modification of the class of an object. Since
we do not want to modify the classes of all instances, we generate a
fresh class for every object, which inherits from our class. This new
class is completely empty, so we can modify it at will. Once we have done
that::

    from karabo.middlelayer_api.injectable import Injectable

    class MyDevice(Injectable, Device):
        @coroutine
        def onInitialization(self):
            # should it be needed to test that the node is there
            self.my_node = None

        @coroutine
        def inject_something(self):
            # inject a new property into our personal class:
            self.__class__.injected_string = String()
            self.__class__.my_node = Node(MyNode, displayedName="position")
            yield from self.publishInjectedParameters()

            # use the property as any other property:
            self.injected_string = "whatever"
            # the test that the node is there is superflous here
            if self.my_node is not None:
                self.my_node.reached = False

    class MyNode(Configurable):
        reached = Bool(displayedName="On position",
                       description="On position flag",
                       defaultValue=True,
                       accessMode=AccessMode.RECONFIGURABLE
        )


Injecting Slots
---------------
Slots are decorating functions.
If you want to add a Slot, or change the function it is bound to (decorating),
the following will do the trick::

    @coroutine
    def very_private(self):
        self.log.INFO("This very private function is now exposed!!")

    @Slot("Inject a slot")
    @coroutine
    def inject_slot(self):
        # Inject a new slot in our schema
        self.__class__.injectedSlot = Slot(displayedName="Injected Slot")
        self.__class__.injectedSlot.__call__(type(self).very_private)
        yield from self.publishInjectedParameters()

.. note::
    They key to that slot will not be `very_private` but instead `injectedSlot`
    So yes, cool that we can change the behaviour of a slot on the fly by
    changing the function the slot calls, but they key won't reflect that.

    If you do change the functions that are called, do put in a log message.

.. warning::
    Before you do that, take a hard look at yourself.
    Consider instead injecting a node with a proper Slot definition.



Note that calling inject_something again resets the values of properties to 
their defaults.
Middlelayer class based injection differs strongly from C++ and
bound api parameter injection, and the following points should
be remembered:

* classes can only be injected into the top layer of the empty class
  and, consequently, of the schema rendition
* the order of injection defines the order in schema rendition
* classes injected can be simple (a Float, Bool, etc.) or complex
  (a node, an entire class hierarchies, etc.)
* later modification of injected class structure is not seen in the
  schema. Modification can only be achieved by overwriting the top level
  assignment of the class and calling `publishInjectedParameters`
* injected classes are not affected by later calls to
  `publishInjectedParameters` used to inject other classes
* deleted (del) injected classes are removed from the schema by calling
  `publishInjectedParameters`





