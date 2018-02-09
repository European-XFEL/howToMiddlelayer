Channels
========
Fast data in karabo is typically shared using p2p channel connections.
This section explores how to share data in such fashion.

The data is send on output channels and received on input channels.
An output channel can send data to several input channels on several devices,
and likewise an input channel can receive data from many outputs.

Ouput Channels
--------------
Firstly, import the required classes::

    from karabo.middlelayer import (
        AccessMode, Configurable, DaqDataType, Float, OutputChannel
    )

Then, define an ouput channel in your device::

    output = OutputChannel(DataNode,
                           displayedName="Output",
                           description="P2P Output channel")

You'll notice that we referenced **DataNode**. This is the schema of our
output channel that defines what data we send and permits other devices 
to manage their expectations.

To define that schema, create a class that inherits from 
`Configurable`::

    class DataNode(Configurable):
        daqDataType = DaqDataType.TRAIN
        floatProperty = Float(defaultValue=0,
                              accessMode=AccessMode.READONLY)

Notice that this class has a variable `daqDataType` defined. This is to 
enable the DAQ to triage the data. The type can either be of PULSE or TRAIN
resolution.

Now that the schema is defined, here's how to send data over the output 
channel::

    @Slot(displayedName="Send P2P Data")
    @coroutine
    def sendP2P(self):
        self.output.schema.floatProperty = 3.5
        yield from self.output.writeData()

Input Channels
--------------
Receiving data from a p2p channel connection is done by decorating a function
with `InputChannel`::

    @InputChannel(displayedName="Input")
    def onInput(self, data, meta):
        print("Data", data)
        print("Meta", meta)

The metadata contains information about the data, such as the source,
whether the data is timestamp, and a timestamp if so.

Good channels share a schema. In the middlelayer API, this is enforced as 
described above. However, devices written in other APIs may not share a schema,
and thus the data has to be treated as *raw*::

    @InputChannel(raw=True, displayedName="Input")
    def onInput(self, data, meta):
        """ Very Important Processing """

For instance, receiving an image from a raw channel is done so::
    
    from karabo.midddlelayer import NDArray

    @InputChannel(raw=True, displayedName="Input")
    def onInput(self, data, meta):
        # Explicitly convert the image data from byte array to numpy array
        image_data = NDArray().toKaraboValue(data["image.data"])
        isinstance(np.array, image_data)  # True

Policies
--------
Different policies can be set at the device level on the behaviour to adopt
when data is arriving too fast on the input channel, or the consumer is too
slow on the output channel.
The various behaviours are:

- queue: put the data in a queue;
- drop: discard the data;
- wait: create a background task that waits until the data can be sent;
- throw: discard the data.

.. note:: 
    
   In other APIs, throw raises an exception, whereas the behaviour here
   is similar to *drop*.

The default is *wait*, which preserves data integrity. 

However, on an output channel, the data will be stored in a buffer, and could 
take up quite some memory would no device connect.
The mode can be set in the GUI, before device instantiation, or as follows::

    self.output.noInputShared = "drop"

The policies are the same on input channels if they are too slow for the fed
data rate, but in copy mode only::

    self.onInput.onSlowness = "drop"

Timing informations
-------------------

.. note:: 

    The following requires functionalities currently in development, that are
    not yet available in the framework, and might be subject to changes
    until release.

At device instantiation, set `useTimeserver` to `True` and `timeServerId` to an
instance of a time server.

Then, generate a Timestamp matching your data, and send it along::

    @Slot(displayedName="Send P2P Data")
    @coroutine
    def sendP2P(self):
        ts = self.getActualTimestamp()
        self.output.schema.floatProperty = 3.6
        yield from self.output.writeData(timestamps=ts)

The timestamp will contain the complete information of epoch time and train id.
On an input channel, the timing information is included in the meta data.

Reference Implementation
------------------------
A reference implementation can be found in pipeML_, where both receiving and
sending data is shown.

A use of middlelayer pipeline can be found in karabacon_.

.. _pipeML: https://git.xfel.eu/gitlab/karaboDevices/pipeML
.. _karabacon: https://git.xfel.eu/gitlab/karaboDevices/Karabacon
