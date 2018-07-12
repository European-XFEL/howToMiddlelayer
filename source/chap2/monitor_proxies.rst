Middlelayer device with proxies
###############################
MonitorMotor is a middle layer device documenting best practice for
monitoring a single `remote device`, that is, a device written with either
of the C++ or Python API.

In this example, the device will initialise a `connection` with a `remote motor
device`, restart the connection if the remote device disappears or resets, and
display the `motorPosition` integer property of that device.

This example introduces the concepts of `Device, connectDevice, isAlive,
waitUntilNew,` and `wait_for`.

Base Class
++++++++++
We begin by creating our class, inheriting from `Device`:
::
    from karabo.middlelayer import Device, State

    class MonitorMotor(Device):

        def __init__(self, configuration):
            #Boilerplate initialisation
            super(MonitorMotor, self).__init__(configuration)

        @coroutine
        def onInitialization(self):
            self.state = State.INIT

:class:`Device` is the base class for all middle layer devices. It inherits from
:class:`~karabo.middlelayer.Configurable` and thus you can define expected
parameters for it.


Connecting to the Remote Device
+++++++++++++++++++++++++++++++
To connect to the remote device, we must have its name, as registered with
the broker, in this example, it is registered as "some_server/1_device_1".

We must first import the :func:`connectDevice` function
::
    from karabo.middlelayer import connectDevice, Device, State

    REMOTE_ADDRESS = "some_server/1_device_1"

Device are typically connected to only once during the initialisation, using
:func:`karabo.middlelayer.connectDevice`
::
    def __init__(self, configuration):
        #Boilerplate initialisation
        super(MonitorRemote, self).__init__(configuration)
        self.remoteDevice = None

    @coroutine
    def onInitialization(self):
        self.state = State.INIT
        self.status = "Waiting for external device"
        self.remoteDevice = yield from connectDevice(REMOTE_ADDRESS)
        self.status = "Connection established"
        self.state = State.STOPPED

This function keeps the connection open until explicitly closing it.
For a more local and temporary usage, :func:`karabo.middlelayer.getDevice`, can
be used within a :class:`with` statement:
::
    with getDevice(REMOTE_ADDRESS) as remote_device:
        print(remote_device.property)


Continuous Monitoring
+++++++++++++++++++++
You now have a connection to a remote device! You may start awaiting its
updates by defining a slot and using the waitUntilNew function
::
    from asyncio import coroutine
    from karabo.middlelayer import connectDevice, State, waitUntilNew
    ...

    @Slot(displayedName="Start",
          description="Start monitoring the remote device",
          allowedStates={State.OFF})
    @coroutine
    def start(self):
        self.state = State.ON
        while True:
            yield from waitUntilNew(self.remoteDevice.remoteValue)
            print(self.remoteDevice.remoteValue)

By doing a `yield from` in  the waitUnitNew coroutine, a non-blocking wait
for the updated value of the property we want is executed before proceeding
to the print statement.

Reconnecting After a Mishap
+++++++++++++++++++++++++++
It may happen that, for some reason, the remote device gets reinitialized,
such as after a server restart.
With the current implementation, we will be automatically notified
and our proxy is reconnected automatically.

Controlling Several Device
##########################

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

    MOTOR_1 = "motor_server/motor_1"
    MOTOR_2 = "motor_server/motor_2"
    MOTOR_3 = "motor_server/motor_3"

    class ControlMotors(Device):

        motor1Pos = Int32(
            displayedName="Motor 1 position",
            description="The current position for Motor 1",
            accessMode=AccessMode.READONLY
        )
        motor2Pos = Int32(
            displayedName="Motor 2 position",
            description="The current position for Motor 2",
            accessMode=AccessMode.READONLY
        )
        motor3Pos = Int32(
            displayedName="Motor 3 position",
            description="The current position for Motor 3",
            accessMode=AccessMode.READONLY
        )

        def __init__ self, configuration):
            super(ControlMotors, self).__init__(configuration)
            self.device_addresses = {MOTOR_1, MOTOR_2, MOTOR_3}
            self.reconnecting = False

        @coroutine
        def onInitialization(self):
            self.state = State.INIT
            devices_to_connect = [connectDevice(device) for device
                                  in self.device_addresses]
            connections = yield from gather(*devices_to_connect)


By using :func:`karabo.middlelayer.gather` and
:func:`karabo.middlelayer.background`, we simultaneously execute all the tasks
in `devices_to_connect` and await their outcomes.


Monitoring Multiple Sources
+++++++++++++++++++++++++++
Monitoring multiple resources is done very much the same way as monitoring a
single one, passing a list of devices as a starred expression:

.. code-block:: Python

    @coroutine
    def monitorPosition(self):
        while True:

            positions_list = [dev.position for dev in self.devices]
            yield from waitUntilNew(*positions_list)

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
::
    yield from setWait(device, targetPosition=42)

It may be desirable to do so, when the parameter needs to be set before further
action should be taken. In this example, setting the desired target position is
done with setWait such that we proceed to moving the motor `only after` the
device has acknowledged the new target position.

As with properties, functions are directly called. To move the motor to the
aforementioned position, call the move function:
::
    self.remoteMotor.move()

Once the parameters are set, :func:`karabo.middlelayer.background` can be used
to run the task:
::
    background(self.remoteMotor.move())

This will create a :class:`KaraboFuture` object of which the status can easily
be tracked or cancelled.

As with reconnections, expending this methodology to cover several devices is
done using :func:`gather`:

.. code-block:: Python

    @coroutine
    def moveSeveral(self, positions):
        futures = []

        for device, position in zip(self.devices, positions):
            yield from setWait(device, targetPosition=position)
            futures.append(device.move())

        yield from gather(*futures)

Exception Handling with Multiple Sources
++++++++++++++++++++++++++++++++++++++++
A problem that now arises is handling exception should one of the motors
develop an unexpected behaviour or, more commonly, a user cancelling the task.
Cancellation raises an :class:`asyncio.CancelledError`, thus extending the above
function with a try-except:
::
    def moveSeveral(self, positions):
        futures = []
        for device, position in zip(self.devices, positions):
            yield from setWait(device, targetPosition=position)
            futures.append(device.move())

        try:
            yield from gather(*futures)
            yield from self.guardian_yield(self.devices)

        except CancelledError:
            toCancel = [device.stop() for device in self.devices
                        if device.state == State.MOVING]
            yield from gather(*toCancel)

Note that the appropriate policy to adopt is left to the device developer.

The try-except introduces a :func:`guardian_yield` function. This is required in
order to remain within the :class:`try` statement, such that any cancellation
happening whilst executing the futures, will be caught by the :class:`except`.

The suggested solution for the guardian yield is to wait until all the device go
from their busy state (`State.MOVING`) to their idle (`State.ON`) as follows:
::
    @coroutine
    def guardian_yield(self, devices):
        yield from waitUntil(lambda: self.reconnecting or
                             all(dev.state == State.ON for dev in devices))

The reconnecting flag is there in case something went really wrong, and one of
the devices went offline. It is then not reasonable to expect task completion.

Excellent, you say, but should all of this truly be the device developer's
problem?
Not nessessarily, enters :class:`DeviceNode`
