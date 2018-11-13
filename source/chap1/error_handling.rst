.. _error-handling

Error Handling
==============
Errors happen and When they happen in Python typically an exception is
raised. The best way to do error handling is to use the usual Python
try-except-finally statements.

There are two types of errors to take care of in Middlelayer API:
:class:`CancelledError` and :class:`TimeoutError`

..  code-block:: Python

    from asyncio import CancelledError, TimeoutError, wait_for
    from karabo.middlelayer import connectDevice, Slot

    @Slot()
    async def doSomething(self):
        try:
            # start something here, e.g. move some motor
        except CancelledError:
            # handle error
        finally:
            # something which should always be done, e.g. move the motor
            # back to its original position

    @Slot()
    async def doOneMoreThing(self):
        try:
            await wait_for(connectDevice("some_device"), timeout=2)
        except TimeoutError:
            # notify we received a timeout error
        finally:
            # reconnect to the device

Sometimes, however, an exception may be raised unexpectedly and has no ways of
being handled better. :func:`onException` is a mechanism that can be overwritten
for this usage:

.. code-block:: Python

   async def onException(self, slot, exception, traceback):
       """If an exception happens in the device, and not handled elsewhere,
       it can be caught here.
       """
       self.logger.warn(f"An exception occured in {slot.method.__name__} because {exception}")
       await self.abort_action()


It is also possible that a user or Middlelayer device will cancel a slot call:

.. code-block:: Python

    async def onCancelled(self, slot):
        """To be called if a user cancels a slot call"""
        tasks = [dev.stop() for dev in self.devices()]
        await allCompleted(*tasks)
