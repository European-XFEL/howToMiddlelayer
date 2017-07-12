Connecting and Reconnecting in the Middle Layer
###############################################

MonitorRemote is a middle layer device documenting best practice for
connecting and maintaining connection to a single `remote device`, that is, a
device written with either of the C++ or Python API.

In this example, the device will initialise a `connection` with a `remote
device`, respawn this connection would the remote device disappear or be
restarted, and display the `remoteValue` integer property of that device.

This example introduces the concepts of `Device, connectDevice, isAlive,
waitUntilNew,` and `wait_for`.

Base Class
++++++++++
We begin by creating our class, inheriting from `Device`
::
    from karabo.middlelayer import Device, State

    class MonitorRemote(Device):

    def __init__(self, configuration):
        #Boilerplate initialisation
        super(MonitorRemote, self).__init__(configuration)
        self.state = State.INIT

    @coroutine
    def onInitialization(self):
        continue

:class:`Device` is the base class for all middle layer devices. It inherits from
:class:`~karabo.middlelayer.Configurable` and thus you can define expected
parameters for it.


Connecting to the Remote Device
+++++++++++++++++++++++++++++++
To connect to the remote device, we must have its name, as registered with
the broker, in this example, it is registered as "some_server_device_1".

We must first import the :func:`connectDevice` function
::
    from karabo.middlelayer import connectDevice, Device, State

    REMOTE_DEVICE = "some_server_device_1"

Device are typically connected to only once during the initialisation
::
    def __init__(self, configuration):
        #Boilerplate initialisation
        super(MonitorRemote, self).__init__(configuration)
        self.state = State.INIT
        self.remoteDevice = None

    @coroutine
    def onInitialization(self):
        self.status = "Waiting for external device"
        self.remoteDevice = yield from(connectDevice(REMOTE_DEVICE))
        self.status = "Connection established"
        self.remoteDevice = State.STOPPED


Obtaining Data
++++++++++++++
You now have a connection to a remote device! You may start awaiting its
updates by defining a slot and using the waitUntilNew function
::
    from asyncio import coroutine
    from karabo.middlelayer import connectDevice, State, waitUntilNew
    ...

    @Slot(displayedName="Start",
          description="Start monitoring the remote device",
          allowedStates={State.STOPPED}
    @coroutine
    def start(self):
        self.state = State.STARTED
        while self.state is State.STARTED:
            yield from waitUntilNew(self.remoteDevice.remoteValue)
            print(self.remoteDevice.remoteValue)

On line 11, we do a `yield from` from the waitUnitNew coroutine. By doing
so, we do a non-blocking wait for the updated value of the property we want,
before proceeding to the print statement.

Reconnecting After a Mishap
+++++++++++++++++++++++++++
It may happen that, for some reason, the remote device gets reinitialised,
such as after a server restart.
With the current implementation, we would be left without any mechanism to
recover. When interacting with a single remote device, we could manually
reinitialise ourselves, but this would not scale up.

For this, two things are required: a watchdog system, and a way to reconnect
the lost device, in the background, as to not interrupt other tasks at hand.

A Watchdog
----------
To implement a watchdog, we need the following imports
::
    from asyncio import coroutine, sleep
    for karabo.middlelayer import background, isAlive

The isAlive function allows us to check whether the connection to the remote
 device is still valid. If the remote device is shut down, then isAlive
 will return False.
 Likewise, if the remote device would had been reinitialised,
 then the connection would be invalid, as it would be a different instance.
 Therefore, the isAlive function would return False.

What we want to do in case the device's gone, is to set reconnect to the
device, in the background, so as to not block other tasks, and set a flag,
so that we do not simultaneously do several attempts to reconnect.::
    @coroutine
    def watchdog(self):
        while True:
            yield from sleep(5)
            if self.reconnecting:
                continue
            if not isAlive(self.device):
                background(self.reconnectDevice())

The Reconnect Coroutine
------------------------
Signalling to the user that a connection has been lost, and that we're
attempting a reconnect, is often done by changing state. It is typically
done by going back to an INIT state.
The reconnect coroutine seems to be a good place to do so.

We thus begin by setting the flag that we are reconnecting, to prevent the
watchdog to spawn more reconnection attempts, and then notifying the user of
the status.

We then proceed to use the connectDevice coroutine to instantiate a new
connection, with an added timeout, to fail gracefully, would the device not
be available for a longer period of time, and then try again.::
   @coroutine
    def reconnectDevice(self):
        self.reconnecting = True

        if not self.reconnecting:
            return

        self.state = State.INIT
        self.status = "Lost remote device"
        while self.reconnecting:
            try:
                self.device = yield from wait_for(connectDevice(REMOTE_DEVICE),
                                                  timeout=2)
            except TimeoutError:
                yield from sleep(1)

            finally:
                self.reconnecting = False
                self.status = "Connection established"
                self.state = State.STARTED



Wrap-up
+++++++
Finally, here is the completed monitoring device, capable of connection,
reconnection, and ready for further usage:
.. literalinclude::../mlsource/MonitorRemote.py
