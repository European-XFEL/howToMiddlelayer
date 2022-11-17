.. _device-attributes:

Karabo Attributes
=================

This section describes how ``attributes`` can be used in **Properties** and **Slots**.

Slots have two important attributes that regulate their access using states and access
modes.

Required Access Level
+++++++++++++++++++++

The ``requiredAccessLevel`` attribute allows to set at which access level this
property may be reconfigured or Slot may be executed.
The minimum ``requiredAccessLevel`` for a reconfigurable property or Slot is at
least `USER (level 1)` if not explicitly specified.

Furthermore, this feature can be used to hide features from lower level users and
some user interfaces might hide information depending on the access level.

User levels are defined in :class:`karabo.middlelayer.AccessLevel`, and range
from `OBSERVER (level 0)` to `ADMIN (level 4)`.
Consequently, a user with lower level access, such as `OPERATOR
(level 2)`, will have access to less information than `EXPERT (level 3)`.

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

    The default requiredAccesslevel is ``AccessLevel.OBSERVER`` (level 0).

Allowed States
++++++++++++++

The middlelayer API of Karabo uses a simple state machine to protect
slot execution and property reconfiguration. Therefore, it is possible to
restrict slot calls to specific states using the `allowedStates` attribute
in the ``Slot`` definition.

States are provided and defined in the Karabo Framework in :class:`karabo.middlelayer.State`

In the example below, the voltage of the controller can only be ramped up
if the device is in the state: :class:`State.ON`.
In the Slot *rampUp* we also switch the device state to `State.RUNNING`,
since a ramp up action will be running after the first call. With this protection,
the procedure of ramping up the device can only be executed again after it has finished.

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

.. note::

    By default every property and Slot may be reconfigured or executed for **all**
    device states.

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

    The default `accessMode` is ``AccessMode.RECONFIGURABLE``. The read only
    setting of a property has to be provided explicitly.


Assignment
++++++++++

The `assignment` attribute declares the behavior of the property on instantiation
of the device. Its function is coupled to the `accessMode`.
It can be either **OPTIONAL**, **MANDATORY** or **INTERNAL**.

Init only properties can only be modified during before instantiation of the
device.

These assignments are very import in the configuration management.

- **INTERNAL** assigned properties are always erased from configuration and indicate that they are provided
  from the device internals on startup.
  This is made visible to the operator, they cannot be edited for example in the graphical user interface.

- **MANDATORY** assigned properties must be provided on instantiation. They are typically left blank,
  and the operator must provide a value (e.g. host, ip for a camera).

.. code-block:: Python

    from karabo.middlelayer import AccessMode, Assignment, Double, String

    # assignment have no effect
    currentVoltage = Double(
        accessMode=AccessMode.READONLY,
        requiredAccessLevel=AccessLevel.OPERATOR)

    # default assignment is OPTIONAL
    targetVoltage = Double(
        defaultValue=20.0
        requiredAccessLevel=AccessLevel.EXPERT)

    # default accessMode is RECONFIGURABLE
    # on instantiation, this property is MANDATORY and must be provided
    host = String(
        assignment = Assignment.MANDATORY,
        requiredAccessLevel=AccessLevel.EXPERT)

    # default accessMode is RECONFIGURABLE
    # on instantiation, this property is INTERNAL. In this case it is read
    # from hardware, but it can be reconfigured on the online device
    targetCurrent = Double(
        assignment = Assignment.INTERNAL,
        requiredAccessLevel=AccessLevel.ADMIN)

.. note::

    The default `assignment` is ``Assignment.OPTIONAL``.

DAQ Policy
++++++++++

Not every parameter of a device is interesting to record.
**As a workaround for a missing DAQ feature**, the policy for each individual
property can be set, on a per-class basis.

These are specified using the :class:`karabo.middlelayer.DaqPolicy` enum:

 - `OMIT`: will not record the property to file;
 - `SAVE`: will record the property to file;
 - `UNSPECIFIED`: will adopt the global default DAQ policy. Currently, it is set to
   record, although this will eventually change to not recorded.

Legacy devices which do not specify a policy will have an `UNSPECIFIED` policy set
to all their properties.

.. note::
    This are applied to leaf properties. Nodes do not have DaqPolicy.

.. code-block:: Python

   from karabo.middlelayer import DaqPolicy

    currentVoltage = Double(
        accessMode=AccessMode.READONLY,
        requiredAccessLevel=AccessLevel.OPERATOR,
        daqPolicy=DaqPolicy.SAVE)

Handling Units
++++++++++++++

You can define a unit for a property, which is then used in the
calculations of this property. In the Middlelayer API units are implemented
using the ``pint`` module.

A unit is declared using the ``unitSymbol`` and further extended with the
``metricPrefixSymbol`` attribute:

.. code-block:: Python

    distance = Double(
        unitSymbol=Unit.METER,
        metricPrefixSymbol=MetricPrefix.MICRO)
    times = VectorDouble(
        unitSymbol=Unit.SECOND,
        metricPrefixSymbol=MetricPrefix.MILLI)
    speed = Double(
        unitSymbol=Unit.METER_PER_SECOND)
    steps = Double()

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
They are used to show what the device is currently doing, what it can do, and
which actions are not allowed.

For instance, it can be disallowed to call the ``start`` slot if the device is
in :class:`State.STARTED` or :class:`State.ERROR`.
Such control can be applied to both slot calls and properties.

The states and their hierarchy are documented in the Framework_.

Within the Middlelayer API, the :class:`State` is an enumerable represented as
string, with a few specific requirements, as defined in
:class:`karabo.middlelayer_api.device.Device`

Although not mandatory, a device can specify which states are used in the ``options``
attribute:

.. code-block:: Python

   from karabo.middlelayer import Overwrite, State

   state = Overwrite(
        defaultValue=State.STOPPED,
        displayedName="State",
        options={State.STOPPED, State.STARTED, State.ERROR})

If this is not explicitly implemented, all states are possible.

State Aggregation
+++++++++++++++++

If you have several proxies, you can aggregate them together and have a global
state matching the most significant. In the example, this is called `trumpState`
and makes use of :func:`karabo.middlelayer.StateSignifier`.

.. code-block:: Python

   from karabo.middlelayer import background, StateSignifier

   async def onInitialization(self):
       self.trumpState = StateSignifier()
       monitor_task = background(self.monitor_states())

   async def monitor_states(self):
       while True:
           # Here self.devices is a list of proxies
           state_list = [dev.state for dev in self.devices]
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
          state = self.remote_device.state
          self.remoteState != state:
            self.remoteState = state:


Tags and Aliases
================

It is possible to assign a property with tags and aliases.

- Tags can be multiple per property and can therefore be used to group properties
together.
- Aliases are unique and for instance used to map hardware commands to Karabo property names.

These are typically used both together without the need for keeping several
lists of parameters and modes.

To begin, mark the properties as desired, here are properties that are polled
in a loop, and properties that are read once, at startup, for instance:

.. code-block:: Python

   from karabo middlelayer import AccessMode, Bool, String
   
   isAtTarget = Bool(displayedName="At Target",
                     description="The hardware is on target position",
                     accessMode=AccessMode.READONLY
                     alias="SEND TARGET",  # The hardware command
                     tags={"once", "poll"})  # The conditions under which to query

   hwStatus = String(displayedName="HW status",
                     description="status, as provided by the hardware",
                     accessMode=AccessMode.READONLY,
                     alias="SEND STATUS",  # The hardware command
                     tags={"poll"})  # The conditions under which to query

   hwVersion = String(displayedName="HW Version",
                      description="status, as provided by the hardware",
                      accessMode=AccessMode.READONLY,
                      alias="SEND VERSION",  # The hardware command
                      tags={"once"})  # The conditions under which to query

Tags of a property can be multiple, and are contained within a set.

Once this is defined, :func:`karabo.middlelayer.Schema.filterByTags` will
return a hash with the keys of all properties having a specific tag:

.. code-block:: Python

   async def onInitialization(self):
       schema = self.getDeviceSchema()
       
       # Get all properties that are to be queried once
       onces = schema.filterByTags("once")     
       # This returns a Hash which is the subset of the current configuration,
       # with the property names that have 'once' as one of their tags.

       # Get the hardware commands, aliases, for each of the properties
       tasks = {prop: self.query_device(schema.getAliasAsString(prop)) for prop in once.keys()}

       # Query
       results = await gather(tasks)

       # Set the result
       for prop, value in results.items():
           setattr(self, prop, value)
   

whilst a background task can poll the other parameters in a loop:

.. code-block:: Python

   from karabo.middlelayer import background, gather

   async def onStart(self):
       schema = self.getDeviceSchema()
       # Get all properties that are to be polled
       to_poll = schema.filterByTags("poll")

       # Create a background loop 
       self.poll_task = background(self.poll(to_poll))
    
       
    async def poll(self, to_poll):
        while True:
            # Get the hardware commands for each of the properties
            tasks = {prop: self.query_device(schema.getAliasAsString(prop)) for prop in to_poll.keys()}

            # Query
            results = await gather(tasks)

            # Set the result
            for prop, value in results.items():
                setattr(self, prop, value)

.. note::
    The concepts of background and gather are explained later in chapter 2

Reference Implementation
------------------------
* OphirPowerMeter_ is a device interfacing with a meter over tcp making use of
  tags and aliases

.. _Framework: https://in.xfel.eu/readthedocs/docs/karabo/en/latest/library/states.html
.. _OphirPowerMeter: https://git.xfel.eu/gitlab/karaboDevices/OphirPowerMeter

