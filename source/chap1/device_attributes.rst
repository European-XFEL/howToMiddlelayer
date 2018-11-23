.. _device-attributes

Property and Slot Attributes
============================

This section describes how attributes can be used in **Properties** and **Slots**.

Slots have two parameters that regulate their access using states and access
modes.

Required Access Level
+++++++++++++++++++++
The `requiredAccessLevel` attribute allows to set at which user level this
property may be reconfigured or Slot may be executed.
For example, when a logged in user does not trump the access level of a slot,
this slot will not be displayed in the *Configurator* of the *Karabo GUI*,
nor will it be available for use in a scene.
This can be used to hide features from lower level users.

User levels are defined in :class:`karabo.middlelayer.AccessLevel`, and range
from `OBSERVER (level 0)` to `ADMIN (level 4)`.
Consequently, a user with lower level access, such as `OPERATOR
(level 2)`, will have access to less information than and `EXPERT (level 3)`.

First, import :class:`AccessLevel`:

.. code-block:: Python

    from karabo.middlelayer import AccessLevel

In the following example, we create a Slot and a property for a voltage
controller whose access is limited to the expert level, such that operators
or users cannot modify the device.
The definition of such a slot is then as follows:

.. code-block:: Python

    targetVoltage = Double(
        defaultValue=20.0
        requiredAccessLevel=AccessLevel.EXPERT)

    @Slot(displayedName="Ramp Voltage up",
          requiredAccessLevel=AccessLevel.EXPERT)
    async def rampUp(self):
        self.status = "Ramping up voltage"

        ... do something

.. note::

    The default requiredAccesslevel is `OBSERVER (level 0)`.

Allowed States
++++++++++++++
In a similar philosophy, it is possible to limit slot calls to specific states
using the `allowedStates` attribute in the Slot definition.

States are provided and fixed in the Karabo Framework. They are defined
in :class:`karabo.middlelayer.State`

The voltage of our controller can only be ramped up if the device is in the
state: :class:`State.ON`. In the ramp up we also switch the state, since a ramp
up action will be already running after the first call.
Then the slot definition will be updated as follows:

.. code-block:: Python

    targetVoltage = Double(
        defaultValue=20.0
        requiredAccessLevel=AccessLevel.EXPERT,
        allowedStates={State.ON})

    @Slot(displayedName="Ramp Voltage up",
          requiredAccessLevel=AccessLevel.EXPERT
          allowedStates={State.ON})
    async def rampUp(self):
        self.status = "Ramping up voltage"

        self.state = State.RUNNING
        ... do something

It is possible to define an arbitrary quantity of states:

.. code-block:: Python

          allowedStates={State.ON, State.OFF}

Note that if the list is empty, then the slot will never be callable.

.. note::

    By default every property and Slot may reconfigured or executed for all
    states, respectively.

AccessMode
++++++++++
The `accessMode` attribute allows to set if a property in a device is a
**READONLY**, **RECONFIGURABLE** or **INITONLY**.

Init only properties can only be modified during before instantiation of the
device.

First, import :class:`AccessMode`:

.. code-block:: Python

    from karabo.middlelayer import AccessMode

Based on the previous example, we add a read only property for the current
voltage of our voltage controller:

.. code-block:: Python

    currentVoltage = Double(
        accessMode=AccessMode.READONLY,
        requiredAccessLevel=AccessLevel.OPERATOR)

    targetVoltage = Double(
        defaultValue=20.0
        requiredAccessLevel=AccessLevel.EXPERT)

.. note::

    The default `accessMode` is `RECONFIGURABLE`, hence the read only nature
    nature of a property has to be explicitly provided.

Handling units
++++++++++++++
You can define a unit for a property, which is then used in the
calculations of this property. In the Middlelayer API, units, amongst other
things, are implemented using the ``pint`` module.

A unit is declared using the ``unitSymbol`` and optionally, the
``metricPrefixSymbol`` attributes:

.. code-block:: Python

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
attribute:

.. code-block:: Python

    self.speed = self.steps * (unit.meters / unit.seconds)
    self.steps = self.distance / (3.5 * unit.meters)

.. warning::

    While the Middlelayer API of Karabo in principle allows for automatic
    unit conversion, developers are strongly discouraged to use this feature for
    critical applications: the Karabo team simply cannot guarantee that
    ``pint`` unit handling is preserved in all scenarios, e.g. that a unit
    is not silently dropped.


Device States
=============
Every device has a state, one of these defined in :class:`karabo.middlelayer.State`.
These are used to show what the device is currently doing, what it can do, and
which actions are restricted.

For instance, it can be disallowed to call the ``start`` slot if the device is
in :class:`State.STARTED` or :class:`State.ERROR`.
Such control can be applied to both slot calls and properties.

The states and their hiearchy are documented in the `Framework`__.


Within the Middlelayer API, the :class:`State` is an eumerable represented as
string, with a few specific requirements, as defined in
:class:`karabo.middlelayer_api.device.Device`

Although not mandatory, a device can specify which states are legal for it:

.. code-block:: Python

   from karabo.middlelayer import Overwrite, State

   state = Overwrite(defaultValue=State.STOPPED,
                     displayedName="State",
                     options={State.STOPPED, State.STARTED, State.ERROR})

If this is not explicitly implemented, the device can go to any state.

State Aggregation
-----------------
If you have several proxies, you can aggregate them together and have a global
state matching the most significant. This is colloquially called `trumpState`
and makes use of :func:`karabo.middlelayer.StateSignifier`.

.. code-block:: Python

   from karabo.middlelayer import background, StateSignifier

   async def onInitialization(self):
       self.trumpState = StateSignifier()
       monitor_taks = background(self.monitor_states())

   async def monitor_states(self):
       while True:
           state_list = [dev.state for dev in self.devices]  # Where self.devices is a list of proxies
           self.state = self.trumpState.returnMostSignificant(state_list)
           await waitUntilNew(*state_list)

As well as getting the most significant state, it will attach the newest
timestamp to the returned state.

It is also possible to define your own rules, as documented in
:class:`karabo.common.states.StateSignifier`


The following shows how to represent and query a remote device's state and
integrate it in a device:

.. code-block:: Python

   from karabo.middlelayer import (
       AccessMode, Assignment, background, connectDevice, State, String,
       waitUntilNew)

   remoteState = String(
       displayedName="State",
       enum=State,
       displayType="State",  # This type enables color coding in the GUI
       description="The current state the device is in",
       accessMode=AccessMode.READONLY,
       assignment=Assignment.OPTIONAL,
       defaultValue=State.UNKNOWN)

   async def onInitialization(self):
       self.remote_device = await connectDevice("some_device")
       self.watch_task = background(self.watchdog())

   async def watchdog(self):
      while True:
          await waitUntilNew(self.remote_device)
          self.remoteState = self.remote_device.state

However, :ref:`device-node` might be more appropriate

.. _framework-states: https://in.xfel.eu/readthedocs/docs/karabo/en/latest/concepts/states.html
__ framework-states_
