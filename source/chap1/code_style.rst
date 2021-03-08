Code Style
==========

While PEP8_, PEP20_, and PEP257_ are stylings to follow, there are a few
Karabo-specific details to take care of to improve code quality, yet keep
consistency, for better maintainability across Karabo's 3 APIs.

An example of a major exception from PEP8_ is that underscores should never be
used for public device properties or slots.

Imports
+++++++

Imports follow `isort` style: they are first in resolution order (built-ins,
external libraries, Karabo, project), then in import style (`from imports`,
`imports`), then in alphabetical order:

.. code-block:: Python

   import sys
   from asyncio import wait_for

   import numpy as np

   from karabo.middlelayer import (
       connectDevice, Device, Slot, String)

   from .scenes import control, default

`isort` can automatically fix imports by calling it with the filename:

.. code-block:: bash

    $ isort Keithley6514.py
    Fixing /data/danilevc/Keithley6514/src/Keithley6514/Keithley6514.py


Class Definitions
+++++++++++++++++

Classes should be `CamelCased`:

.. code-block:: Python

   class MyDevice(Device):
       pass

Abbreviations in class names should be capitalised:

.. code-block:: Python

   class JJAttenutator(Device):
       pass

   class SA3MirrorsWitch(Device):
       pass

Class Properties
++++++++++++++++

Properties part of the device's schema, which are exposed, should be
`camelCased`, whereas non-exposed variables should `have_underscores`:

.. code-block:: Python

   name = String(displayedName="Name")

   someOtherString = String(
       displayedName="Other string",
       defaultValue="Hello",
       accessMode=AccessMode.READONLY)

   valid_ids = ["44eab", "ff64d"]


Slots and Methods
+++++++++++++++++

Slots are `camelCased`, methods `have_underscores`.
Slots must not take arguments, apart from `self`.

.. code-block:: Python

   @Slot(displayedName='Execute')
   async def execute(self):
       """This slot is exposed to the system"""
       self.state = State.ACTIVE
       await self.execute_action()

   @Slot(displayedName='Abort',
         allowedStates={State.ACTIVE, State.ERROR})
   async def abortNow(self):
       self.state = state.STOPPING
       await self.abort_action()

   async def execute_action(self):
       """This is not exposed, and therefore PEP8"""
       pass

Mutable objects must not be used as default values in method
definitions.

Printing and Logging
++++++++++++++++++++

Logging is the way to share information to developers and maintainers.
This allows for your messages to be stored to files for analysis at a later
time, as well as being shared with the GUI under certain conditions.

The Middlelayer API has its own `Logger` implemented as a :class:`Configurable`.
It is part of the Device class and no imports are required.

Whilst it can be used either as `self.log` or `self.logger`, the preferred
style is as follows:

.. code-block:: Python

   from karabo.middlelayer import allCompleted

   async def stop_all(self):
       self.logger.info("Stopping all devices")
       tasks = [device.stop() for device in self.devices]
       done, pending, failed = await allCompleted(*tasks)
       if failed:
           self.logger.error("Some devices could not be stopped!")

.. note::
    Logging is disabled in the constructor :func:`__init__`.

Inplace Operators
+++++++++++++++++

Inplace operations on Karabo types are discouraged for reasons documented in
:ref:`timestamping`.

Don't do:

.. code-block:: Python

   speed = Int32(defaultValue=0)

   @Slot()
   async def speedUp(self):
       self.speed += 5

But rather:

.. code-block:: Python

   speed = Int32(defaultValue=0)

   @Slot()
   async def speedUp(self):
       self.speed = self.speed.value + 5


Exceptions
++++++++++

It is preferred to check for conditions to be correct rather than using
exceptions. This defensive approach is to ensure that no device would be stuck
or affect other devices running on the same server.

Therefore, the following is discouraged:

.. code-block:: Python


   async def execute_action(self):
       try:
           await self.px.move()
       except:
           pass

But rather:

.. code-block:: Python

   async def execute_action(self):
       if self.px.state not in {State.ERROR, State.MOVING}:
           await self.px.move()
       else:
           pass

If exceptions are a must, then follow the :ref:`error-handling`

Use Double and NOT Float
++++++++++++++++++++++++

The middlelayer API supports both `Double` and `Float` properties.

However, behind the scenes a `Float` value is casted as numpy's `float32` type.
Casting this value back to float64 may lead to different value. Hence, services
on top of the framework might cast this value to a string before casting to the
built-in python float of 64 bit to prevent cast errors.
Note, that a 32 bit float has a precision of 6, which might be of different
expectation for a normal python developer.

**Use `karabo.middlelayer.Double` instead of `Float`.**

.. _PEP8: https://www.python.org/dev/peps/pep-0008/
.. _PEP20: https://www.python.org/dev/peps/pep-0020/
.. _PEP257: https://www.python.org/dev/peps/pep-0257/
