Pipelining Channels
===================
Fast or big data in Karabo is typically shared using Pipeline Channel
connections.
This section explores how to share data in such fashion.

The data is sent on output channels and received on input channels.
An output channel can send data to several input channels on several devices,
and likewise an input channel can receive data from many outputs.

Output Channels
---------------
Firstly, import the required classes:

.. code-block:: Python

    from karabo.middlelayer import (
        AccessMode, Configurable, DaqDataType, Double, Node, OutputChannel
    )

Then, define an output channel in your device:

.. code-block:: Python

    output = OutputChannel(ChannelNode,
                           displayedName="Output",
                           description="Pipeline Output channel")

You'll notice that we referenced **ChannelNode**. This is the schema of our
output channel that defines what data we send and permits other devices
to manage their expectations.

To define that schema, create a class that inherits from
`Configurable`:

.. code-block:: Python

    class DataNode(Configurable):
        daqDataType = DaqDataType.TRAIN

        doubleProperty = Double(
            defaultValue=0.0,
            accessMode=AccessMode.READONLY)

    class ChannelNode(Configurable):
        data = Node(DataNode)

Notice that this class has a variable `daqDataType` defined. This is to
enable the DAQ to triage the data. The type can be of either PULSE or TRAIN
resolution and has to be encapsulated in the Node.

Now that the schema is defined, here's how to send data over the output
channel:

.. code-block:: Python

    @Slot(displayedName="Send Pipeline Data")
    async def sendPipeline(self):
        self.output.schema.data.doubleProperty = 3.5
        await self.output.writeData()

Alternatively, we can send a Hash without setting the property on the device:

.. code-block:: Python

    @Slot(displayedName="Send Pipeline Raw Data")
    async def sendPipelineRaw(self):
        await self.output.writeRawData(Hash('data.doubleProperty', 3.5))


Input Channels
--------------
Receiving data from a Pipeline Channel is done by decorating a function
with `InputChannel`:

.. code-block:: Python

    @InputChannel(displayedName="Input")
    async def input(self, data, meta):
        print("Data", data)
        print("Meta", meta)

The metadata contains information about the data, such as the source,
whether the data is timestamped, and a timestamp if so.

If the device developer is interested in the bare Hash of the data, one can
set the *raw* option to True:

.. code-block:: Python

    @InputChannel(raw=True, displayedName="Input")
    async def input(self, data, meta):
        """ Very Important Processing """

For image data it is recommended to use the **raw=False** option, as the
middlelayer device will automatically assign an NDArray to the ImageData,
accessible via:

.. code-block:: Python

    @InputChannel(displayedName="Input")
    async def input(self, data, meta):
        image = data.data.image

If it is needed to use the bare Hash in the case of ImageData, it can be converted to NDArray as:

.. code-block:: Python

    @InputChannel(raw=True, displayedName="Input")
    async def input(self, data, meta):
        img_raw = data["data.image.pixels"]
        img_type = img_raw["type"]
        dtype = numpy.dtype(Type.types[img_type].numpy)
        shape = img_raw["shape"]
        image = numpy.frombuffer(img_raw["data"], dtype=dtype).reshape(shape)

It is possible to react on the **endOfStream** or the **close** signal
from the output channel via:

.. code-block:: Python

    @input.endOfStream
    async def input(self, channel):
        print("End of Stream handler called by", channel)

    @input.close
    async def input(self, channel):
        print("Close handler called by", channel)


Policies
--------
Different policies can be set at the device level on the behaviour to adopt
when data is arriving too fast on the input channel, or the consumer is too
slow on the output channel.
The various behaviours are:

- queue: put the data in a queue;
- drop: discard the data;
- wait: create a background task that waits until the data can be sent;
- throw: discard the data when serving the data, raises an exception when
        receiving.

The default is *wait*, which preserves data integrity.

The mode can be set in the GUI, before device instantiation, or as follows::

    self.output.noInputShared = "drop"

The policies are the same on input channels if they are too slow for the fed
data rate, but in copy mode only::

    self.input.onSlowness = "drop"


Reference Implementation
------------------------
A reference implementation can be found in pipelineMDL_, where both receiving
and sending data is shown.

.. _pipelineMDL: https://git.xfel.eu/gitlab/karaboDevices/pipelineMDL
