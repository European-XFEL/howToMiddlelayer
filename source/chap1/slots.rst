Karabo Slots
============

Often, it is needed to define a :class:`Slot`, associated to a function, perhaps
for users to start a device:
::

    @Slot(displayedName="Start",
          description="Prints an integer",
          allowedStates={State.OFF})
    @coroutine
    def start(self):
        self.state = State.ON

        i = 0
        while True:
            yield from sleep(1)
            print(i)
            i = i + 1

Note that two decorators are used: :class:`karabo.middlelayer.Slot` and
:class:`asyncio.coroutine`.

The ordering of these matter: a **golden rule** in a middlelayer device is to
decorate slot functions with a coroutine.
The slot exits with the last state update and returns once the code is run
through.

Decorators wrap the function they are decorating, and really are syntax sugar,
and are executed from the closest, to the furthest: **@coroutine** is called
first, and then **@Slot**.

The above slot is thus excecuted as:
::

    Slot(coroutine(start), **kwargs)

and not
::

    coroutine(Slot(start, **kwargs))

Changes in the ordering will result in code that will run, but lead to
**undefined behaviours**.

Keeping a Slot (Return with correct state)
++++++++++++++++++++++++++++++++++++++++++
In certain cases, it may be useful to keep a slot, to prevent a user to
interfere with current operation, for example. Since slots are asynchronous,
some trickery is required. For simplicity, below is an example assuming we read
out the motor states in a different task.

::

    @coroutine
    def state_monitor():
        # A simple state monitor
        while True:
            yield from waitUntilNew(self.motor1.state, self.motor2.state)
            state = StateSignifier().returnMostSignificant(
                [self.motor1.state, self.motor2.state])
            if state =! self.state:
                self.state = state

    @Slot(displayedName="Move",
          description="Move a motor",
          allowedStates={State.ON})
    @coroutine
    def move(self):

        # We move to motors at once
        yield from gather(self.motor1.move(), self.motor2.move())
        # We wait for our own state change here to exit this slot with
        # the expected state, e.g. ERROR or MOVING.
        yield from waitUntil(lambda: self.state != State.ON)

