from karabo.middlelayer import Device, Int32, String, waitUntil


class Motor(Device):
    """This is a motor that has shared access to a controller talking
    to hardware"""

    controllerId = String()
    channelId = Int32(defaultValue=1)

    async def onInitialization(self):
        """This method is executed on instantiation"""

        def is_online():
            return self.getLocalDevice(self.controllerId.value) is not None

        await waitUntil(lambda: is_online)
        # A bit less readable example with 2 lambdas
        await waitUntil(lambda: lambda: self.getLocalDevice(
            self.controllerId.value) is not None)
        # Strong reference to the controller device
        controller = self.getLocalDevice(self.controllerId.value)
        # Call a function directly on the device object
        values = await controller.read_hardware_values(self.channelId)
