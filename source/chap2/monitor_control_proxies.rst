Start simple: A single proxy
============================
We recapitulate our knowledge and start simple by creating our device class,
inheriting from `Device`:

.. code-block:: Python

    from karabo.middlelayer import Device, State

    class MonitorMotor(Device):

        def __init__(self, configuration):
            super(MonitorMotor, self).__init__(configuration)

        async def onInitialization(self):
            self.state = State.INIT

:class:`Device` is the base class for all middle layer devices. It inherits from
:class:`~karabo.middlelayer.Configurable` and thus you can define expected
parameters for it.

Connecting to the Remote Device
+++++++++++++++++++++++++++++++
To connect to the remote device, we must have its control address.
In this example, it is registered as "SA1_XTD9_MONO/MOTOR/X".

We must first import the :func:`connectDevice` function:

.. code-block:: Python

    from karabo.middlelayer import connectDevice, Device, State

    REMOTE_ADDRESS = "SA1_XTD9_MONO/MOTOR/X"

Device are typically connected to only once during the initialisation, using
:func:`karabo.middlelayer.connectDevice`:

.. code-block:: Python

    def __init__(self, configuration):
        super(MonitorRemote, self).__init__(configuration)
        self.remoteDevice = None

    async def onInitialization(self):
        self.state = State.INIT
        self.status = "Waiting for external device"
        self.remoteDevice = await connectDevice(REMOTE_ADDRESS)
        self.status = "Connection established"
        self.state = State.STOPPED

This function keeps the connection open until explicitly closing it.
For a more local and temporary usage, :func:`karabo.middlelayer.getDevice`, can
be used:

.. code-block:: Python

    with (await getDevice(REMOTE_ADDRESS)) as remote_device:
        print(remote_device.property)

.. note::
    The ``async with`` statement is not yet supported in Karabo

Continuous Monitoring
+++++++++++++++++++++
You now have a connection to a remote device! You may start awaiting its
updates by defining a slot and using the waitUntilNew function

.. code-block:: Python

    from karabo.middlelayer import connectDevice, State, waitUntilNew
    ...

    @Slot(displayedName="Start",
          description="Start monitoring the remote device",
          allowedStates={State.OFF})
    async def start(self):
        self.state = State.ON
        while True:
            await waitUntilNew(self.remoteDevice.remoteValue)
            print(self.remoteDevice.remoteValue)

By awaiting the :func:`waitUnitNew` coroutine, a non-blocking wait
for the updated value of the property is executed before proceeding
to the print statement.

.. note::

    It may happen that the remote device gets reinitialized, e.g. the underlying
    device of the proxy is gone, such as after a server restart.
    The proxy will automatically switch the state property to **State.UNKNOWN**
    once the device is gone and reestablish all connections when it comes back.

Grow stronger: Several proxies in a device
==========================================
Now that a device can be remotely monitored, and the connection kept alive,
let's see how to connect to several devices at once, and then control them.

In this example, we will build upon the previous chapter and initialise
several connections with three `remote motor devices`, get their positions,
and set them to a specific position.

The concepts of `gather`, `background` are introduced here.

Multiple Connection Handling
++++++++++++++++++++++++++++
In order to handle several devices, we must make a few changes to the watchdog
and reconnection coroutines.


Let us define three motors we want to monitor and control:

.. code-block:: Python
   from asyncio import gather
   from karabo.middlelayer import background

    MOTOR_1 = "SA1_XTD9_MONO/MOTOR/X"
    MOTOR_2 = "SA1_XTD9_MONO/MOTOR/Y"
    MOTOR_3 = "SA1_XTD9_MONO/MOTOR/Z"

    class ControlMotors(Device):

        motor1Pos = Int32(
            displayedName="Motor 1 position",
            description="The current position for Motor 1",
            accessMode=AccessMode.READONLY)

        motor2Pos = Int32(
            displayedName="Motor 2 position",
            description="The current position for Motor 2",
            accessMode=AccessMode.READONLY)

        motor3Pos = Int32(
            displayedName="Motor 3 position",
            description="The current position for Motor 3",
            accessMode=AccessMode.READONLY)

        def __init__ self, configuration):
            super(ControlMotors, self).__init__(configuration)
            self.device_addresses = {MOTOR_1, MOTOR_2, MOTOR_3}

        async def onInitialization(self):
            self.state = State.INIT
            devices_to_connect = [connectDevice(device) for device
                                  in self.device_addresses]
            connections = await gather(*devices_to_connect)


By using :func:`asyncio.gather` and
:func:`karabo.middlelayer.background`, we simultaneously execute all the tasks
in `devices_to_connect` and await their outcomes.


Monitoring Multiple Sources
+++++++++++++++++++++++++++
Monitoring multiple resources is done very much the same way as monitoring a
single one, passing a list of devices as a starred expression:

.. code-block:: Python

    async def monitorPosition(self):
        while True:
            positions_list = [dev.position for dev in self.devices]
            await waitUntilNew(*positions_list)

            motorPos1 = self.devices[0].position
            motorPos2 = self.devices[1].position
            motorPos3 = self.devices[2].position


Controlling Multiple Sources
++++++++++++++++++++++++++++
Setting properties of a device is done directly by assigning the property a
value, for instance:

.. code-block:: Python

    self.remoteMotor.targetPosition = 42

This guarantees to set the property. It is possible, however, to do a blocking
wait, using :func:`setWait`:

.. code-block:: Python

    await setWait(device, targetPosition=42)

It may be desirable to do so, when the parameter needs to be set before further
action should be taken. In this example, setting the desired target position is
done with setWait such that we proceed to moving the motor `only after` the
device has acknowledged the new target position.

As with properties, functions are directly called. To move the motor to the
aforementioned position, await the :func:`move` function:

.. code-block:: Python

    await self.remoteMotor.move()

Once the parameters are set, :func:`karabo.middlelayer.background` can be used
to run the task:

.. code-block:: Python

    background(self.remoteMotor.move())

This will create a :class:`KaraboFuture` object of which the status can easily
be tracked or cancelled.

As with reconnections, expending this methodology to cover several devices is
done using :func:`gather`:

.. code-block:: Python

    async def moveSeveral(self, positions):
        futures = []

        for device, position in zip(self.devices, positions):
            await setWait(device, targetPosition=position)
            futures.append(device.move())

        await gather(*futures)

Exception Handling with Multiple Sources
++++++++++++++++++++++++++++++++++++++++
A problem that now arises is handling exception should one of the motors
develop an unexpected behaviour or, more commonly, a user cancelling the task.
Cancellation raises an :class:`asyncio.CancelledError`, thus extending the above
function with a try-except:

.. code-block:: Python

    async def moveSeveral(self, positions):
        futures = []
        for device, position in zip(self.devices, positions):
            await setWait(device, targetPosition=position)
            futures.append(device.move())
        try:
            await gather(*futures)
            await self.guardian_yield(self.devices)
        except CancelledError:
            toCancel = [device.stop() for device in self.devices
                        if device.state == State.MOVING]
            await gather(*toCancel)


.. note::

    Note that the appropriate policy to adopt is left to the device developer.

The try-except introduces a :func:`guardian_yield` function. This is required in
order to remain within the :class:`try` statement, such that any cancellation
happening whilst executing the futures, will be caught by the :class:`except`.

The suggested solution for the guardian yield is to wait until all the device go
from their busy state (`State.MOVING`) to their idle (`State.ON`) as follows:

.. code-block:: Python

    async def guardian_yield(self, devices):
        await waitUntil(lambda: all(dev.state == State.ON for dev in devices))


