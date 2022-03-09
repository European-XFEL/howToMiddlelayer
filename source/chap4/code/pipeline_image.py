from asyncio import sleep

import numpy as np

from karabo.middlelayer import (
    AccessMode, background, Configurable,
    DaqDataType, Device, Image, Int32, Node, OutputChannel, Slot,
    UInt8, UInt32, State)


def channelSchema(dtype):
    """Return the output channel schema for a `dtype`"""

    class DataNode(Configurable):
        daqDataType = DaqDataType.TRAIN

        image = Image(displayedName="Image",
                      dtype=dtype,
                      shape=(800, 600))

    class ChannelNode(Configurable):
        data = Node(DataNode)

    return ChannelNode


class ImageMDL(Device):
    output = OutputChannel(
        channelSchema(UInt32),
        displayedName="Output")

    frequency = Int32(
        displayedName="Frequency",
        defaultValue=2)

    imageSend = UInt32(
        displayedName="Packets Send",
        defaultValue=0,
        accessMode=AccessMode.READONLY)

    def __init__(self, configuration):
        super(ImageMDL, self).__init__(configuration)
        self._dtype = UInt32

    async def onInitialization(self):
        self.state = State.ON
        self._acquiring = False
        background(self._network_action())

    @Slot(allowedStates=[State.ACQUIRING])
    async def stop(self):
        self.state = State.ON
        self._acquiring = False

    @Slot(allowedStates=[State.ON])
    async def start(self):
        self.state = State.ACQUIRING
        self._acquiring = True

    @Slot(displayedName="Reset Counter")
    async def resetCounter(self):
        self.imageSend = 0

    @Slot(displayedName="Send EndOfStream", allowedStates=[State.ON])
    async def writeEndOfStream(self):
        await self.output.writeEndOfStream()

    @Slot(displayedName="Set Image data dtype")
    async def setImageDtype(self):
        """Example method to show how output channel can be changed on
        runtime"""
        dtype = UInt8 if self._dtype == UInt32 else UInt32
        self._dtype = dtype
        schema = channelSchema(dtype)
        # provide key and new schema
        await self.setOutputSchema("output", schema)

    async def _network_action(self):
        while True:
            if self._acquiring:
                output = self.output.schema.data
                # Descriptor classes have `numpy` property
                dtype = self._dtype.numpy
                image_array = np.random.randint(
                    0, 255, size=(800, 600),
                    dtype=dtype)
                output.image = image_array
                self.imageSend = self.imageSend.value + 1
                await self.output.writeData()

            await sleep(1 / self.frequency.value)
