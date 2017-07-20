Decorators and their order
==========================
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

The ordering of these matter: a middlelayer slot expects a coroutine, such
that it can be run without blocking other tasks.

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

Keeping a Slot
==============
In certain cases, it may be useful to keep a slot, to prevent a user to
interfere with current operation, for example. Since slots are asynchronous,
some trickery is required.


