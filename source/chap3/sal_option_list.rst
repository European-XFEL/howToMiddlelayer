State and Access Mode Options
=============================

Slots have two parameters that regulate their access using states and access
modes.

Required Access Level
+++++++++++++++++++++
Called `accessMode` in the bound APIs, the `requiredAccessLevel`
parameter allows to set which level of user has access to the slot.
When a user does not have access to a slot, this slot will not be displayed in
the *Configuration Editor* panel, nor will it be available for use in a scene.
This can be used to hide features from lower level users.

User levels are defined in :class:`karabo.middlelayer.AccessLevel`, and range
from `OBSERVER` to `GOD`. A user with lower level access, such as `OPERATOR
(level 2)`, will have access to less information than and `EXPERT (level 3)`.

First, import :class:`AccessLevel`:

.. code-block:: Python

    from karabo.middlelayer import AccessLevel

Let's say a slot that loads the current device configuration from a file should
be limited to an expert, such that operators or users cannot mistakenly modify
the device.
The definition of such a slot is then as follows:

.. code-block:: Python

    @Slot(displayedName="Load configuration file",
          requiredAccessLevel=AccessLevel.EXPERT)
    @coroutine
    def loadConfigFromFile(self):
        self.status = "Loading config..."

        with open("filename", "r") as f:
            self.config = f.read()

        self.status = "Config loaded"

States Option List
++++++++++++++++++
In a similar philosophy, it is possible to limit slot calls to specific states
using the `allowedStates` parameter in the slot definition.

States are defined in :class:`karabo.middlelayer.State`

.. warning:: Do not define your own states. It may seem appealing, but this will
             break Karabo in the most critical moment.


Say a device has four states: :class:`State.ON`, :class:`State.OFF`,
:class:`State.RUNNING`,  and :class:`State.STOPPED`, and the aforementioned
:func:`loadConfigFromFile` should callable only when the device is
:class:`State.OFF`, then the slot definition will be updated as follows:

.. code-block:: Python

    @Slot(displayedName="Load configuration file",
          requiredAccessLevel=AccessLevel.EXPERT,
          allowedStates=[State.OFF])
    @coroutine
    def loadConfigFromFile(self):
        self.status = "Loading config..."

        with open("filename", "r") as f:
            self.config = f.read()

        self.status = "Config loaded"


It is possible to define an arbitrary quantity of states:

.. code-block:: Python

          allowedStates=[State.OFF, State.STOPPED]

Note that if the list is empty, then the slot will never be callable.
