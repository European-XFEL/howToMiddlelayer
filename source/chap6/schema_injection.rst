Schema injection
================

A parameter injection is a modification of the class of an object. Since
we do not want to modify the classes of all instances, we generate a
fresh class for every object, which inherits from our class. This new
class is completely empty, so we can modify it at will. Once we have done
that::

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


Note that calling inject_something again resets the values of proprties to their defaults.
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





