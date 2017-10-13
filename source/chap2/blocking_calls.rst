Blocking Calls: Using Synchronous Functions within Coroutines
=============================================================

Within a coroutine, regular functions that take a long time to run
need to be wrapped in a particular way.

Background
++++++++++

`karabo.middlelayer.background` is a function that allows to run either
coroutines as background tasks, or regular synchronous functions without
stalling other parts of the device.

How to use background to run coroutines as background tasks is explained in
chapter 3: connect_reconnect in the watchdog example.

To handle a synchronous function, background is given the function, *without
brackets*, and any arguments used by that function:

.. code-block:: Python

    from time import sleep
    from karabo.middlelayer import background
    # Do a blocking sleep for a second
    background(sleep, 1)

NB. outside of this example, `asyncio.sleep` really should be used.

Note that `background` does not support keyworded arguments. As such, all
arguments need to be provided:

.. code-block:: Python

    def func(from_=None, to=None, protocol=pickle, msg=""):
        pass

    # Instead of:
    func(from_=me, to=you, msg=message)
    # do:
    background(func, me, you, None, message)

Example Implementation
++++++++++++++++++++++

The `caller_` device mixes synchronous and asynchronous calls in all possible
ways:
    * coroutines are called normally.

    * `background` is used within `onInitialization` to start the
      `monitor` coroutine as a permanent background task.

    * `background` is used within `emergencyCall` to allow the use
      of a synchronous third-party library (`calls.create` and
      `messages.create`).

    * the simpler `get_human_time` function does not need to be wrapped as a
      background task, as its result is returned quasi-instantly.

.. _caller: http://in.xfel.eu/gitlab/karaboDevices/caller

