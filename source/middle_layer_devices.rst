**********************
Karabo middlelayer API
**********************

The Karabo ``middlelayer`` API is written in pure `Python <http://www.python.org>`_
deriving its name from the main design aspect: controlling and monitoring
driver devices while providing state aggegration and additional functionality.
The same interface is also used for the macros.
Hence, this api exposes an efficient interface for tasks such as
interacting with other devices via device proxies to enable monitoring of properties,
executing commands and waiting on their completion, either synchronously
or asynchronously.


Start simple: Hello World!
==========================

Below is the source code of a Hello World! device::

    from asyncio import coroutine
    from karabo.middlelayer import Device, Slot, String


    class HelloWorld(Device):

        __version__ = "1.0"

        greeting = String(
            defaultValue="Hello World!",
            description="Message printed to console.")

        @Slot()
        def hello(self):
            print(self.greeting)

        @coroutine
        def onInitialization(self):
            """ This method will be called when the device starts.

                Define your actions to be executed after instantiation.
            """
            pass

The middlelayer device is created by inheriting from the middlelayer's ``Device`` base class.
A class property `__version__` can indicate the lowest Karabo version in which this device is supposed to run.
In this device we create a Karabo property `greeting` which is
Here we create a single slot by decorating a member function accordingly. This
will render as a button labeled "hello" in the GUI or be accessible using
``remote().execute("/some/remote/device", "hello")`` from the CLI.

.. note::

    It recommended to explicitly specify imports as shown in the example, rather than
    using ``from foo import \* ``.


The device ``HelloYou`` now has a string expected parameter, which is rendered in the GUI
as a text box, and accessible from the CLI via ``remote().get("InstanceID", "name")``.
Attributes assignable in the expected parameter declarations of the ``core`` APIs may also
be specified in the middlelayer API property definitions::

Property Attributes
+++++++++++++++++++

Attributes of properties may be accessed during runtime as members of the property descriptor.

+------------------+------------------------------------------------------------------------------------+
|**Attribute**     |  **Example**                                                                       |
+------------------+------------------------------------------------------------------------------------+
| Display type     | self.property.descriptor.displayType  # returns oct, bin, dec, hex                 |
+------------------+------------------------------------------------------------------------------------+
| Min value        | self.property.descriptor.minInc  # the inclusive-minimum value                     |
|                  +------------------------------------------------------------------------------------+
|                  | self.property.descriptor.minExc  # the exclusive-minimum value                     |
+------------------+------------------------------------------------------------------------------------+
| Max value        | self.property.descriptor.maxInc  # the inclusive-maximum value                     |
|                  +------------------------------------------------------------------------------------+
|                  | self.property.descriptor.maxExc  # the exclusive-maximum value                     |
+------------------+------------------------------------------------------------------------------------+
| Warnings         | self.property.descriptor.warnLow  # values below or equal to this cause a warning  |
|                  +------------------------------------------------------------------------------------+
|                  | self.property.descriptor.warnHigh  # values above or equal to this cause a warning |
+------------------+------------------------------------------------------------------------------------+
| Alarms           | self.property.descriptor.alarmLow  # values below or equal to this cause an alarm  |
|                  +------------------------------------------------------------------------------------+
|                  | self.property.descriptor.alarmHigh  # values above or equal to this cause an alarm |
+------------------+------------------------------------------------------------------------------------+
| Variance         | self.property.descriptor.warnVarHigh  # the maximum variance value                 |
|                  +------------------------------------------------------------------------------------+
| (Warnings)       | self.property.descriptor.warnVarLow  # the minimum variance value                  |
+------------------+------------------------------------------------------------------------------------+
| Variance         | self.property.descriptor.alarmVarHigh  # the maximum variance value                |
|                  +------------------------------------------------------------------------------------+
| (Alarms)         | self.property.descriptor.alarmVarLow  # the minimum variance value                 |
+------------------+------------------------------------------------------------------------------------+
| Unit             | self.property.descriptor.unitSymbol  # e.g. Unit.METER                             |
|                  +------------------------------------------------------------------------------------+
|                  | self.property.descriptor.metricPrefixSymbol  # e.g. MetricPrefix.MILLI             |
+------------------+------------------------------------------------------------------------------------+
| Unit scale       | self.property.descriptor.unitScale  # the key of property holding the scale        |
+------------------+------------------------------------------------------------------------------------+
| Access modes     | self.property.descriptor.accessMode  # e.g. AccessMode.READONLY                    |
+------------------+------------------------------------------------------------------------------------+
| Assignment       | self.property.descriptor.assignment  # e.g. Assignment.OPTIONAL                    |
+------------------+------------------------------------------------------------------------------------+
| Default value    | self.property.descriptor.defaultValue  # the default value or None                 |
+------------------+------------------------------------------------------------------------------------+
| Access level     | self.property.descriptor.requiredAccessLevel  # e.g. AccessLevel.EXPERT            |
+------------------+------------------------------------------------------------------------------------+
| Allowed states   | self.property.descriptor.allowedStates  # the list of allowed states               |
+------------------+------------------------------------------------------------------------------------+
