.. _overwrite:

Overwrite Properties
====================

Classes in Karabo may have default properties. A type of motors may have a
default speed, a camera may have a default frame rate, and so forth.

Let's say a base class for a motor has a default max speed of 60 rpms:

.. code-block:: Python

    class MotorTemplate(Configurable):
        maxrpm = Int32(
                    displayedName="Max Rotation Per Minutes",
                    accessMode=AccessMode.READONLY,
                    allowedStates={State.ON},
                    unitSymbol=Unit.NUMBER)
        maxrpm = 60

        ...[much more business logic]...

All instances of that MotorTemplate will have a fixed maximum rpm 60, that can
be seen when the state is State.ON, and is read only.

We now would like to create a custom motor, for a slightly different usage,
where users can set this maximum, according to their needs, but all other
parameters and functions remain the same.

It is possible to do so by inheriting from :class:`MotorTemplate`, and using the
:class:`karabo.middlelayer.Overwrite` element:

.. code-block:: Python

    class CustomMotor(MotorTemplate):
        maxrpm = Overwrite(
                    minExc=1,
                    accessMode=AccessMode.RECONFIGURABLE,
                    allowedStates={State.OFF, State.INIT})

Note that only the required fields are modified. Others, such as
:class:`displayedName` will retain their original values.

Using :class:`Overwrite` allows inheritance whilst replacing pre-existing
parameters, keeping the namespace clean, and avoiding confusion between the
local and inherited scope, thus providing a simpler codebase.


