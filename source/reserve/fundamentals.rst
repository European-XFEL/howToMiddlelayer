****************************
Middlelayer API Fundamentals
****************************

The design of the Karabo Middle-Layer API
=========================================
In Karabo, every device has a *schema*, which contains all the details
about the expected parameters, its types, comments, units, everything.
It is only broadcast rarely over the network, typically only during
the initial handshake with the device. Once the schema is known, only
*configurations*, or even only parts of configurations, are sent over
the network in a tree structure called *Hash* (which is not a hash
table).

These configurations know nothing anymore about the meaning of the
values they contain, yet they are very strictly typed: even different
bit sizes of integers are conserved.

The Karabo basetypes
--------------------

The Karabo basetypes were designed to ease the use of all the features
of Karabo expected parameters, namely the fact that they have units
and timestamps. Given that most devices in a scientific control system
are typically written in a very rapid prototyping manner, and given
that one of Karabo's goals is to enable many users to quickly write
proper Karabo devices, it is obvious that most device programmers
won't care about proper treatment of timestamps, let alone units.

This is why we do that automatically. For the unit part, we use
:mod:`pint`, while the timestamps part had to be written by us.


Device server: Eventloop
========================

Karabo middlelayer uses Python's asyncio, installing a custom event loop.
All devices in a device server share the same event loop which is run in a
single thread. Hence, every blocking call in any device instance results in
blocking every other device in the same device server.
However, the device developer is free to start threads using background, which
starts a thread if used with a function which is not a coroutine.
The event loop thread pool executor can have 200 threads.


Bulk-set of properties
======================

In a synchronous context, setting a parameter is synchronous, hence the code blocks
until the parameter is properly set or an error is raised.

In a coroutine, however, all parameter settings are automatically cached and will
not be sent before the next ``yield from``. It is guaranteed that parameter
settings are properly ordered and are sent before the next slot call in bulk.

As a corollary, setting a parameter multiple times results in only one
setting on the device of the last value. If this is not desired, use update
device as follows::

    proxy.someValue = 3
    yield from updateDevice(proxy)
    proxy.someValue = 5



Synchronized Functions
======================

There are many functions in Karabo which do not instantaneously execute.
Frequently, it is important that other code can continue running
while such a function is still executing. For the ease of
use, all those functions, which are documented here as
**synchronized**, follow the same calling convention, namely, they have
a set of additional keyword parameters to allow for non-blocking calls to them:

timeout
    gives a timeout in seconds. If the function is not done after
    it timed out, a ``TimeoutError`` will be raised, unless the
    timeout is -1, meaning infinite timeout. The executed function
    will be canceled once it times out.

callback
    instead of blocking until the function is done, it returns
    immediately. Once the function is done, the supplied callback
    will be executed. The function returns a ``Future`` object,
    described below; the callback will get the same
    future object passed as its only parameter.

    If callback is ``None``, the function still returns immediately
    a future, but no callback is called.

What is a Karabo Future
=======================

The future object contains everything to manage asynchronous
operations:

.. py:class:: Future

    .. py:method:: cancel()

        Cancel the running function. The running function will stop
        executing as soon as possible.

    .. py:method:: cancelled()

        Return whether the function was canceled

    .. py:method:: done()

        Return whether the function is done, so returned normally,
        raised an exception or was canceled.

    .. py:method:: result()

        Return the result of the function, or raise an error if the
        function did so.

    .. py:method:: exception()

        Return the exception the function raised, or ``None``.

    .. py:method:: add_done_callback(cb)

        Add a callback to be run once the function is done. It gets passed
        the future as the single parameter.

    .. py:method:: wait()

        wait for the function to finish


Tasks: background
=================

You can call your own ``synchronized`` functions and launch them in the
background:

.. py:function:: background(func, *args, **kwargs)

   Call the function *func* with *args* and *kwargs*.

   The function passed is wrapped as a ``synchronized`` function.
   In a very simple description the *func* gets called in the background.

   The background function will create and return a task which can
   be cancelled. A ``CancelledError`` is raised in the called function,
   which allows you to react to the cancellation, including ignoring it::

    @Slot(displayedName="Start",
          description="Starts task")
    @coroutine
    def start(self):
        self.task = background(self.start_scan)

    @Slot(displayedName="Stop",
          description="Stops task")
    @coroutine
    def stop(self):
        if self.task:
            self.task.cancel()
            self.task = None

    @coroutine
    def start_scan(self):
        try:
            ... do something here ...
        except CancelledError:
            ... react on cancellation ...

.. note::

    :func:`background` creates and runs a thread if and only if the passed function is not a
    coroutine, otherwise the coroutine is simply scheduled on the event loop.


Sleep nicely!
=============

You should always prefer the middlelayer ``sleep`` function over
``time.sleep``. The asyncio sleep can be canceled and is not a blocking call.

.. py:function:: sleep(delay)

   Stop execution for at least *delay* seconds.

   This is a ``synchronized`` function, so it may also be used to
   schedule the calling of a callback function at a later time.

.. note::

   If a unit is provided, the sleep function will account for it.

Locking
=======

A locked device will only allow read-only access to its properties by a
device not holding the lock. Similarly command execution is
restricted to the lock holder::

    @Slot(displayedName="Perform X-scan")
    @coroutine
    def perform(self):
        with getDevice("some_device") as device:
            with (yield from lock(device)):
                # do something useful here


.. py:function:: lock(device)

   lock the *device* for exclusive use by this owner device.

   The function returns a context manager to be used in a ``with``
   statement.

   The parameter ``lockedBy`` of a device contains the current owner
   of the lock, or an empty string if nobody holds a lock.


Synchronous or Asynchronous
===========================

Although property access via device proxies is usually to be preferred, there are scenarios
where only a single or very few interactions with a remote device are necessary. In such
a case the following shorthands may be used::

   yield from setWait("deviceId", "someOtherParameter", a)
   yield from execute("deviceId", "someSlot")

The aforementioned commands are blocking and synchronized coroutines.

Additionally, non-blocking methods are provided, indicated by the suffix ``NoWait`` to
each command::

   def callback(deviceId, parameterName, value):
       #do something with value
       ...

   setNoWait("deviceId", "someOtherParameter", a)
   executeNoWait("deviceId", "someSlot", callback=callback)

As shown in the code example a non-blocking property retrieval is realized by supplying
a callback when the value is available. The callback for ``executeNoWait`` is optional and
will be triggered when the execute completes.

The ``executeNoWait`` method without callback is internally implemented by sending
a fire-and-forget signal to the remote device.

If a callback is given, instead a blocking signal is launched in co-routine,
triggering the callback upon completion. The ``executeNoWait`` call will immediately
return though.

