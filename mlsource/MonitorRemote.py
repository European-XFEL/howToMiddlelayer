from asyncio import coroutine, sleep, TimeoutError, wait_for

from karabo.middlelayer import (AccessMode, background, connectDevice, Device,
                                isAlive, Int32, Slot, State, waitUntilNew)

REMOTE_DEVICE = "remote_server1/remote_dev0"


class MonitorRemote(Device):
    """
    MonitorRemote is a middle layer device documenting best practice for
    connecting and reconnecting to a `remote device`. That is, a device
    written with either of the C++ or Python API.
    """
    remoteValue = Int32(
        displayedName="External value",
        description="The current value on external device",
        accessMode=AccessMode.READONLY
    )

    def __init__(self, configuration):
        super(MonitorRemote, self).__init__(configuration)

        self.state = State.INIT
        self.device = None
        self.reconnecting = False

    @coroutine
    def onInitialization(self):
        self.status = "Waiting for external device"
        self.device = yield from(connectDevice(REMOTE_DEVICE))
        self.status = "Connection established"

        background(self.watchdog())
        self.state = State.STOPPED

    @Slot(displayedName="Start",
          description="Start monitoring the remote device",
          allowedStates={State.STOPPED})
    @coroutine
    def start(self):
        self.state = State.STARTED
        while self.state != State.STOPPED:
            self.remoteValue = self.device.x
            yield from waitUntilNew(self.device.x)

    @Slot(displayedName="Stop",
          description="Stop monitoring the remote device",
          allowedStates={State.STARTED})
    @coroutine
    def stop(self):
        self.state = State.STOPPED

    @coroutine
    def reconnectDevice(self):

        if self.reconnecting:
            return

        self.reconnecting = True
        self.state = State.INIT
        self.status = "Lost remote device"

        while self.reconnecting:
            try:
                self.device = yield from wait_for(connectDevice(REMOTE_DEVICE),
                                                  timeout=2)
                self.reconnecting = False
                self.status = "Connection established"
                self.state = State.STARTED

            except TimeoutError:
                yield from sleep(1)

    @coroutine
    def watchdog(self):
        while True:
            yield from sleep(7)
            if self.reconnecting:
                continue
            if not isAlive(self.device):
                background(self.reconnectDevice)