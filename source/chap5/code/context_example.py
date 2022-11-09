import pytest
import uuid

from karabo.middlelayer import Device, Slot, String, connectDevice, isSet
from karabo.middlelayer.testing import (
    AsyncDeviceContext, create_device_server, event_loop)


def create_instanceId():
    return f"test-mdl-{uuid.uuid4()}"


class WW(Device):
    name = String()

    def __init__(self, configuration):
        super().__init__(configuration)
        self.destructed = False

    @Slot()
    async def sayMyName(self):
        self.name = "Heisenberg"

    async def onDestruction(self):
        self.destructed = True


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_example_context(event_loop: event_loop):
    # Make sure to create unique instance id's
    deviceId = create_instanceId()
    device = WW({"_deviceId_": deviceId})
    ctx_deviceId = create_instanceId()
    ctx_device = WW({"_deviceId_": ctx_deviceId})

    # Use the device context class to instantiate devices
    async with AsyncDeviceContext(device=device) as ctx:
        devices = ctx.instances
        assert not isSet(device.name)
        assert not isSet(devices["device"].name)
        proxy = await connectDevice(deviceId)
        await proxy.sayMyName()
        assert device.name == "Heisenberg"
        assert proxy.name == "Heisenberg"
        assert devices["device"].name == "Heisenberg"
        assert len(devices) == 1
        # A new device can always be added to the stack for instantiation
        # and shutdown
        await ctx.device_context(new=ctx_device)
        assert len(devices) == 2
        assert ctx_device.destructed is False
        assert device.destructed is False

    # The context destroys all devices on exit
    assert ctx_device.destructed is True
    assert device.destructed is True


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_example_server_context(event_loop: event_loop):
    """Example how to start and create a server"""
    serverId = create_instanceId()
    # The server can be created with a list of device classes
    server = create_device_server(serverId, [WW])
    async with AsyncDeviceContext(server=server) as ctx:
        server_instance = ctx.instances["server"]
        assert server_instance.serverId == serverId
        # The class name appears in the server plugins and can be used to
        # instantiate devices
        assert "WW" in server_instance.plugins
