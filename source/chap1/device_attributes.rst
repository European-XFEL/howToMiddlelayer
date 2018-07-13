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
    @coroutine
    def rampUp(self):
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
    @coroutine
    def rampUp(self):
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