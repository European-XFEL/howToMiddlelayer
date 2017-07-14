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

This dichotomy is similar to classes and objects (more precisely: an
object's ``__dict__``) in Python. Similar, but different, which means
that every time data is sent to or received from the network, we have
to do a conversion step. When data is received, we check it for
validity and add all the details that we know from the schema, once
data is sent, we assure all data is converted to the correct unit and
data format, and strip it of all the details.

Setting, sending and receiving parameters
-----------------------------------------

All these conversions are centered around the
:class:`~karabo.middlelayer.Type`. Its main conversion routines are
:meth:`~karabo.middlelayer.Type.toKaraboValue` which converts data
from the network or from the user to a
:class:`~karabo.middlelayer.KaraboValue`, and
:meth:`~karabo.middlelayer.Type.toHash`, which converts a Karabo value
to the hash for the network.
:meth:`~karabo.middlelayer.Type.toKaraboValue` has an attribute
*strict* which defines whether the conversion should check exactly the
right unit or whether it simply adds a unit if none exists. The latter
behavior is needed for data coming from the network, as it has no unit
information, while the former behavior is used in case the user
changes the value, who better does proper unit handling.

In total, five different conversions need to
be done: receiving and sending for the current and remote devices, as
well as during initialization:

- When devices change their own properties, Python calls the
  descriptor's :meth:`~karabo.middlelayer.Descriptor.__set__` method.
  This converts the incoming value using the strict
  :meth:`~karabo.middlelayer.Type.toKaraboValue`, thereby checking
  that the value is valid, and attaches the current time as timestamp
  if no timestamp has been given. Then it calls
  :meth:`~karabo.middlelayer.SignalSlotable.setValue` on the
  device, which sets the value in the device's ``__dict__``, and
  also stores it in a :class:`~karabo.middlelayer.Hash` using
  :meth:`~karabo.middlelayer.Descriptor.toHash` to broadcast it
  via :meth:`~karabo.middlelayer.SignalSlotable.signalChanged`.

- During initialization by
  :meth:`~karabo.middlelayer.Configurable.__init__`, the user-supplied
  or default value is passed to
  :meth:`~karabo.middlelayer.Type.initialize`. Its default
  implementation passes this over to the coroutine
  :meth:`~karabo.middlelayer.Type.setter`, which calls
  :func:`setattr`, which hands it over to the usual Python machinery
  just described.

  During initialization, more properties may be set than during a
  normal reconfiguration at runtime. This is why we have to treat it
  as a special case and cannot use the code path for the latter.

  This behavior also allows us to define special properties that do
  something during initialization. As an example, a ``RemoteDevice``
  parameter may already connect to the remote device upon
  initialization. Properly declaring a parameter to refer to a remote
  device instead of a mere string also adds the option for a Karabo
  global initializer to start devices in the right order.

- Devices receive requests to change their configuration through
  :meth:`~karabo.middlelayer.Device.slotReconfigure`. This calls
  :meth:`~karabo.middlelayer.Descriptor.checkedSet` for every parameter to
  be reconfigured, which checks whether it is allowed to modify this
  parameter and raises an error if that's not the case. It converts
  the incoming value using the non-strict
  :meth:`~karabo.middlelayer.Type.toKaraboValue`, which also checks limits,
  and attaches a timestamp if supplied.
  Then it calls the coroutine :meth:`~karabo.middlelayer.Descriptor.setter`,
  and returns the result. :meth:`~karabo.middlelayer.Device.slotReconfigure`
  can then run all the coroutines to change values in parallel.

  This seemingly complicated procedure has several advantages: if the
  user tries to set a read-only (or non-existent) parameter, we
  immediately refuse the entire reconfiguration request, as it is
  obviously wrong. On the other hand, we are still able to have
  setters which take some time, as they are a coroutine.

  For nodes, :meth:`~karabo.middlelayer.Node.checkedSet` recurses into
  the node and calls :meth:`~karabo.middlelayer.Descriptor.checkedSet` for
  its members.

- If a device wants to access another, remote device, it uses a
  subclass of :class:`~karabo.middlelayer.Proxy`. This subclass contains the
  same descriptors as devices. When a user changes a value, the
  proxy's :meth:`~karabo.middlelayer.Proxy.setValue` is called. It converts
  the value using the non-strict
  :meth:`~karabo.middlelayer.Type.toKaraboValue` and attaches the current
  time as timestamp if no other has been given. It will not set the
  value in the object, but instead send the changes to the network
  converting it to a :class:`~karabo.middlelayer.Hash` using
  :meth:`~karabo.middlelayer.Descriptor.toHash`.

- Changes received from a remote device enter through the device's
  :meth:`~karabo.middlelayer.Device.slotChanged`. This will call the
  proxy's :meth:`~karabo.middlelayer.Proxy._onChanged` method. This will
  convert the incoming value using the non-strict
  :meth:`~karabo.middlelayer.Type.toKaraboValue` and attach the timestamp
  from the network, before entering the value into the proxy's
  ``__dict__``.

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
:mod:`pint`, while the timestamps part had to be written by us. The
timestamp itself is just a :class:`~karabo.middlelayer.Timestamp`.
In Karabo, a value is considered valid in an interval, this means the
timestamp gives the start time after which this value is valid, until
the next value arrives.

Handling timestamps
~~~~~~~~~~~~~~~~~~~

When a user operates on a :class:`~karabo.middlelayer.KaraboValue`, the
timestamp of the result is the newest timestamp of all timestamps that
take part in the operation, unless the user explicitly sets a
different one. This is in line with the validity intervals described
above: if a value is composed from other values, it is valid typically
starting from the moment that the last value has become valid (this
assumes that all values are still valid at composition time, but this
is the responsibility of the user, and is typically already the case).

Technically, we automatically wrap all methods of a
:class:`~karabo.middlelayer.KaraboValue` using
:func:`~karabo.middlelayer.basetypes.wrap_function`, which goes through all
attributes to the wrapped function and converts the returned value
into a :class:`~karabo.middlelayer.KaraboValue` using
:func:`~karabo.middlelayer.basetypes.wrap`, attaching the newest timestamps
of the attributes.

In the case of numpy arrays, we instead override
:meth:`~karabo.middlelayer.QuantityValue.__array_wrap__`, which is designed
particularly to do the wrapping job.

Handling descriptors
~~~~~~~~~~~~~~~~~~~~

It might be unnecessary at first sight to store the descriptor of a
value in the value itself, especially as it gets lost immediately when
operating on that value.

But the reason becomes obvious when we want to use device properties
for anything other than their value. Most simply,
``help(device.speed)`` should not show the help for float values,
but actually give help on the device's parameter.

We use this extensively in other parts. As an example,
``waitUntilNew(device.speed)`` wouldn't work if ``device.speed``
wouldn't know where it comes from. For sure, ``3 * device.speed`` has
no relation to the original anymore, so ``waitUntilNew(3 *
device.speed)`` wouldn't make much sense, thus it loses the descriptor.


Eventloop
=========


Bulk-set of properties
======================


Unit Handling
=============

You can define a unit for a property, which is then used in the
calculations of this property. In the middlelayer API, units, amongst other
things, are implemented using the ``pint`` module.

A unit is declared using the ``unitSymbol`` and optionally, the
``metricPrefixSymbol`` attributes::

    distance = Float(
        unitSymbol=Unit.METER,
        metricPrefixSymbol=MetricPrefix.MICRO)
    times = VectorFloat(
        unitSymbol=Unit.SECOND,
        metricPrefixSymbol=MetricPrefix.MILLI)
    speed = Float(
        unitSymbol=Unit.METER_PER_SECOND)
    steps = Float()

Once declared, all calculations have correct units::

    self.speed = self.distance / self.times[3]

In this code units are  converted automatically. An error is
raised if the units don't match up::

    self.speed = self.distance + self.times[2]  # Ooops! raises error

If you need to add a unit to a value which doesn't have one, or remove
it, there is the ``unit`` object which has all relevant units as its
attribute::

    self.speed = self.steps * (unit.meters / unit.seconds)
    self.steps = self.distance / (3.5 * unit.meters)

.. warning::

    While the middlelayer API of Karabo in principle allows for automatic
    unit conversion, developers are strongly discouraged to use this feature for
    critical applications: the Karabo team simply cannot guarantee that
    ``pint`` unit handling is preserved in all scenarios, e.g. that a unit
    is not silently dropped.



Timestamps
==========

All properties in Karabo may have timestamps attached. In the middlelayer API
they can be accessed from the ``timestamp`` attribute::

    self.speed.timestamp

They are automatically attached and set to the current time upon
assignment of a value that does not have a timestamp::

    self.steps = 5  # current time as timestamp attached

A different timestamp may be attached using the ``timestamp``
function::

    self.steps = timestamp(5, "2009-09-01 12:34 UTC")

If a value already has a timestamp, it is conserved, even through
calculations. If several timestamps are used in a calculation, the
newest timestamp is used. In the following code, ``self.speed`` gets
the newer timestamp of ``self.distance`` or ``self.times``::

    self.speed = 5 * self.distance / self.times[3]

.. warning::

    Developers should be aware that automated timestamp handling defaults to the
    newest timestamp, i.e. the time at which the last assignment operation
    on a variable in a calculation occured. Additionally, these timestamps are
    not synchronized with XFEL's timing system, but with the host's local clock.
    If handling of timestamps is a critical aspect of the algorithm being
    implemented it is strongly recommended to be explicit in timestamp handling,
    i.e. use ``speed_timestamp = self.speed.timestamp`` and re-assign this
    as necessary using ``timestamp(value, timestamp).

Synchronized Functions
======================

There are many functions in Karabo which do not instantaneously execute.
Frequently, it is important that other code can continue running
while such a function is still executing. For the ease of
use, all those functions, which are documented here as
*synchronized*, follow the same calling convention, namely, they have
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
+++++++++++++++++++++++

MORE IS REQUIRED HERE. HOW TO IMPORT. MAYBE AN EXAMPLE HOW TO SET THIS

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

What does background do?
++++++++++++++++++++++++

You can call your own synchronized_ functions and launch them in the
background:

.. py:function:: background(func(*args, **kwargs))

   Call the function *func* with *args* and *kwargs*.

   The function passed is wrapped as a synchronized_ function.
   In a very simple description the *func* gets called in the background.



   and the caller is notified
   via a the callback upon completion, with any return values passed as a future.

   The called function can be canceled. This happens the next time it
   calls a synchronized_ function. A ``CancelledError`` is raised in
   the called function, which allows you to react to the cancellation,
   including ignoring it.

    .. note::
        It is not possible to cancel any other operation than calls to
        synchronized_ functions, as interventions in third party code
        are not possible.

Sleep nicely!
+++++++++++++

You should always prefer the middlelayer sleep function over
``time.sleep``. As described above, this sleep can be canceled,
while ``time.sleep`` cannot.

.. py:function:: sleep(delay)

   Stop execution for at least *delay* seconds.

   This is a synchronized_ function, so it may also be used to
   schedule the calling of a callback function at a later time.

   synchronized_ method.


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


.. py:function:: lock(device, timeout=0)

   lock the *device* for exclusive use by this device. If the lock
   cannot be acquired within *timeout* seconds, a ``TimeoutError``
   will be raised. A *timeout* of ``-1`` signifies an unlimited wait.

   the function returns a context manager to be used in a ``with``
   statement.

    The parameter ``lockedBy`` of a device contains the current owner
    of the lock, or an empty string if nobody holds a lock.

.. warning::

    Device locks are not thread-safe locks. If you need
    to lock threads thread-safe, use the appropriate locks from the threading library.

Synchronous or Asynchronous
===========================

Although property access via device proxies is usually to be preferred, there are scenarios
where only a single or very few interactions with a remote device are necessary. In such
a case the following shorthands may be used::

   setWait("deviceId", "someOtherParameter", a)
   execute("deviceId", "someSlot", timeout=10)

The aforementioned commands are blocking and all accept an optional timeout parameter.
They raise a ``TimeoutError`` if the specified duration has passed.

Additionally, non-blocking methods are provided, indicated by the suffix ``NoWait`` to
each command::

   def callback(deviceId, parameterName, value):
       #do something with value
       ...

   setNoWait("deviceId", "someOtherParameter", a)
   executeNoWait("deviceId", "someSlot", callback = callback)

As shown in the code example a non-blocking property retrieval is realized by supplying
a callback when the value is available. The callback for ``executeNoWait`` is optional and
will be triggered when the execute completes.

.. ifconfig:: includeDevInfo is True

    The ``executeNoWait`` method without callback is internally implemented by sending
    a fire-and-forget signal to the remote device.

    If a callback is given, instead a blocking signal is launched in co-routine,
    triggering the callback upon completion. The ``executeNoWait`` call will immediately
    return though.


Error Handling
==============

Errors do happen. When they happen, in Python typically an exception is
raised. The best way to do error handling is to use the usual Python
try-except-statements.

So far we have introduced and taken care of time-out errors. Another recurring situation
is that a user cancels a operation currently in progress. In such cases a ``CancelledError``
is raised:

..  code-block:: Python

    @Slot
    def do_something(self):
        try:
            # start something here, e.g. move some motor
        except CancelledError:
            # clean up stuff
        finally:
            # something which should always be done, e.g. move the motor
            # back to its original position

Sometimes, however, an exception happens unexpectedly, or should be handled in a quite
generic fashion. In either case it might be advisable to bring the system back into a
defined, safe state. This can be done by overwriting the following device methods::

    def onCancelled(self, slot):
        """to be called if a user canceled the operation"""

The ``slot`` is the slot that had been executed.


Injecting Parameters
====================

