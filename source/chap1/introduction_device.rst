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

        __version__ = "2.0"

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

The middlelayer device is created by inheriting from the middlelayer's ``Device`` base class.
Below the device class definition are the expected parameters, containing the static schema of the device.
A property `__version__` can indicate the lowest Karabo version in which this device is supposed to run.
In this device we create a Karabo property `greeting` which is also referred to as ``KaraboValue``.
This property has an assigned ``descriptor`` `String` containing the ``attributes``.
In this example the `defaultValue` and the `description` attributes are defined,
which is rendered in the karabo GUI as a text box showing "Hello World!".

Additionally, we create a single ``Slot`` `hello` by using a decorator.
This slot will be rendered in the karabo GUI as a button enabling us to print
the greeting string to console.

Descriptors
-----------

As shown by the example, every device has a *schema*, which contains all the details
about the expected parameters, its types, comments, units, everything. In the
middlelayer this schema is built by so-called **karabo descriptors**.
A schema is only broadcasted rarely over the network, typically only during
the initial handshake with the device. Once the schema is known, only
*configurations*, or even only parts of configurations, are sent over
the network in a tree structure called *Hash* (which is not a hash
table).

These configurations know nothing anymore about the meaning of the
values they contain, yet they are very strictly typed: even different
bit sizes of integers are conserved.

The following descriptors in the middlelayer api are available for 'simple' types

**Bool**, **Char**, **String**, **ComplexDouble**, **ComplexFloat**, **Double**,
**Float**, **Int8**, **Int16**, **Int32**, **Int64**, **UInt8**, **UInt16**,
**UInt32**, **UInt64**

and for the vector properties:

**VectorBool**, **VectorChar**, **VectorString**, **VectorComplexDouble**,
**VectorComplexFloat**, **VectorDouble**, **VectorFloat**, **VectorInt8**,
**VectorInt16**, **VectorInt32**, **VectorInt64**, **VectorUInt8**,
**VectorUInt16**, **VectorUInt32**, **VectorUInt64**

Attributes
----------

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
| Warnings         | self.property.descriptor.warnLow  # warn threshold low                             |
|                  +------------------------------------------------------------------------------------+
|                  | self.property.descriptor.warnHigh  # warn threshold high                           |
+------------------+------------------------------------------------------------------------------------+
| Alarms           | self.property.descriptor.alarmLow  # alarm threshold low                           |
|                  +------------------------------------------------------------------------------------+
|                  | self.property.descriptor.alarmHigh  # alarm threshold high                         |
+------------------+------------------------------------------------------------------------------------+
| Unit             | self.property.descriptor.unitSymbol  # e.g. Unit.METER                             |
|                  +------------------------------------------------------------------------------------+
|                  | self.property.descriptor.metricPrefixSymbol  # e.g. MetricPrefix.MILLI             |
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


Handling units
--------------

You can define a unit for a property, which is then used in the
calculations of this property. In the middlelayer API, units, amongst other
things, are implemented using the ``pint`` module.

A unit is declared using the ``unitSymbol`` and optionally, the
``metricPrefixSymbol`` attributes::

    distance = Float(
        unitSymbol=Unit.METER,
        metricPrefixSymbol=MetricPrefix.MICRO)
    times = VectorFloat(
        unitSymbol=Unit.SECOND,
        metricPrefixSymbol=MetricPrefix.MILLI)
    speed = Float(
        unitSymbol=Unit.METER_PER_SECOND)
    steps = Float()

Once declared, all calculations have correct units::

    self.speed = self.distance / self.times[3]

In this code units are  converted automatically. An error is
raised if the units don't match up::

    self.speed = self.distance + self.times[2]  # Ooops! raises error

If you need to add a unit to a value which doesn't have one, or remove
it, there is the ``unit`` object which has all relevant units as its
attribute::

    self.speed = self.steps * (unit.meters / unit.seconds)
    self.steps = self.distance / (3.5 * unit.meters)

.. warning::

    While the middlelayer API of Karabo in principle allows for automatic
    unit conversion, developers are strongly discouraged to use this feature for
    critical applications: the Karabo team simply cannot guarantee that
    ``pint`` unit handling is preserved in all scenarios, e.g. that a unit
    is not silently dropped.

Handling timestamps
-------------------

When a user operates on a :class:`~karabo.middlelayer.KaraboValue`, the
timestamp of the result is the newest timestamp of all timestamps that
take part in the operation, unless the user explicitly sets a
different one. This is in line with the validity intervals described
above: if a value is composed from other values, it is valid typically
starting from the moment that the last value has become valid (this
assumes that all values are still valid at composition time, but this
is the responsibility of the user, and is typically already the case).

All properties in Karabo may have timestamps attached. In the middlelayer API
they can be accessed from the ``timestamp`` attribute::

    self.speed.timestamp

They are automatically attached and set to the current time upon
assignment of a value that does not have a timestamp::

    self.steps = 5  # current time as timestamp attached

A different timestamp may be attached using the ``timestamp``
function::

    self.steps.timestamp = Timestamp("2009-09-01 12:34 UTC")

If a value already has a timestamp, it is conserved, even through
calculations. If several timestamps are used in a calculation, the
newest timestamp is used. In the following code, ``self.speed`` gets
the newer timestamp of ``self.distance`` or ``self.times``::

    self.speed = 5 * self.distance / self.times[3]

.. warning::

    Developers should be aware that automated timestamp handling defaults to the
    newest timestamp, i.e. the time at which the last assignment operation
    on a variable in a calculation occured. Additionally, these timestamps are
    not synchronized with XFEL's timing system, but with the host's local clock.
