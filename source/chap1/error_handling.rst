Error Handling
==============

Errors happen and When they happen in Python typically an exception is
raised. The best way to do error handling is to use the usual Python
try-except-statements.

In the middlelayer API we basically have to take care about the ``CancelledError``
and the ``TimeoutError``

..  code-block:: Python

    from asyncio import coroutine, CancelledError, TimeoutError
    from karabo.middlelayer import Slot

    @Slot()
    @coroutine
    def doSomething(self):
        try:
            # start something here, e.g. move some motor
        except CancelledError:
            # clean up stuff
        finally:
            # something which should always be done, e.g. move the motor
            # back to its original position

    @Slot()
    @coroutine
    def doOneMoreThing(self):
        try:
            yield from wait_for(connectDevice("some_device"), timeout=2)
        except TimeoutError:
            # notify we received a timeout error
        finally:
            # reconnect to the device

Sometimes, however, an exception happens unexpectedly, or should be handled in a quite
generic fashion. In either case it might be advisable to bring the system back into a
defined, safe state. This can be done by overwriting the following device methods:

.. code-block:: Python

    def onCancelled(self, slot):
        """to be called if a user canceled the operation"""
        for dev in self.devices:
            yield from dev.disable()
