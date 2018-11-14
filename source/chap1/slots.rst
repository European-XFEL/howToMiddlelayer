Karabo Slots
============

:class:`karabo.middlelayer.Slot` is the way to mark coroutines as actionable
from the ecosystem, whether from the GUI, or other Middlelayer devices:

.. code-block:: Python

   from karabo.middlelayer import Slot

    @Slot(displayedName="Start",
          description="Prints an integer",
          allowedStates={State.OFF})
    async def start(self):
        self.state = State.ON

        i = 0
        while True:
            await sleep(1)
            print(i)
            i = i + 1


A **golden rule** in a Middlelayer device is that :class:`Slot` are coroutines
The slot exits with the last state update and returns once the code is run
through.

:class:`Slot` has a number of arguments that are explained in :ref:`device-attributes`


Holding a Slot (Return with correct state)
++++++++++++++++++++++++++++++++++++++++++
In certain cases, it may be useful to keep a slot, to prevent a user to
interfere with current operation, for example. Since slots are asynchronous,
some trickery is required. For simplicity, below is an example assuming we read
out the motor states in a different task.

.. code-block:: Python

    async def state_monitor():
        # A simple state monitor
        while True:
            await waitUntilNew(self.motor1.state, self.motor2.state)
            state = StateSignifier().returnMostSignificant(
                [self.motor1.state, self.motor2.state])
            if state != self.state:
                self.state = state

    @Slot(displayedName="Move",
          description="Move a motor",
          allowedStates={State.ON})
    async def move(self):

        # We move to motors at once
        await gather(self.motor1.move(), self.motor2.move())
        # We wait for our own state change here to exit this slot with
        # the expected state, e.g. ERROR or MOVING.
        await waitUntil(lambda: self.state != State.ON)

